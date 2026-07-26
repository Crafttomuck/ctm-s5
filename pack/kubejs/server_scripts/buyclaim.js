// /buyclaim — buy OPAC claim capacity with Numismatics coins.
// Players claim chunks on the Xaero map as usual; this command only raises
// their claim limit via OPAC Bonus Claims (/opacbonusclaims claims <player> <n>).
//
// Pricing: first purchased chunk costs BASE_PRICE spurs, each subsequent
// chunk costs 2% more (compound). Purchase count is stored per player in
// persistent data, so escalation survives restarts.
//
// Payment: loose coins in the inventory only — coins inside wallets are not
// counted. Counting/removal uses the KubeJS inventory API directly.
// (Do NOT use server.runCommandSilent('clear ...') to count items — it
// returns a success flag, not the item count.)
//
// Rhino note: const/let declared inside a loop BODY throws "redeclaration
// of var" at runtime, so all loop variables are hoisted above their loops.

const BASE_PRICE = 64 // spurs, price of the first purchased chunk (1 cog)
const GROWTH = 1.02 // 2% compound increase per purchased chunk
const MAX_PER_PURCHASE = 100
const PURCHASED_KEY = 'buyclaim_purchased'

// Ascending order matters: payment is taken smallest-denomination-first.
const COINS = [
    { id: 'numismatics:spur', value: 1 },
    { id: 'numismatics:bevel', value: 8 },
    { id: 'numismatics:sprocket', value: 16 },
    { id: 'numismatics:cog', value: 64 },
    { id: 'numismatics:crown', value: 512 },
    { id: 'numismatics:sun', value: 4096 }
]

// Price of the nth purchased chunk (1-indexed).
function chunkPrice(n) {
    return Math.round(BASE_PRICE * Math.pow(GROWTH, n - 1))
}

// Total price of the next `count` chunks for a player who already purchased `purchased`.
function totalPrice(purchased, count) {
    let total = 0
    for (let i = 1; i <= count; i++) {
        total += chunkPrice(purchased + i)
    }
    return total
}

// Adds `count` bonus claims through the OPAC API and returns the new bonus
// total, or -1 if the change didn't stick. Uses the API directly instead of
// /opacbonusclaims because runCommandSilent returns void in this KubeJS
// build — a silently failing command would look like success.
function grantBonusClaims(player, count) {
    const OpenPACServerAPI = Java.loadClass('xaero.pac.common.server.api.OpenPACServerAPI')
    const PlayerConfigOptions = Java.loadClass('xaero.pac.common.server.player.config.api.PlayerConfigOptions')
    const JInteger = Java.loadClass('java.lang.Integer')
    const cfg = OpenPACServerAPI.get(player.server).getPlayerConfigs().getLoadedConfig(player.uuid)
    const spec = PlayerConfigOptions.BONUS_CHUNK_CLAIMS
    const before = cfg.getEffective(spec)
    const result = cfg.tryToSet(spec, JInteger.valueOf(before + count))
    const after = cfg.getEffective(spec)
    if (after != before + count) {
        console.error(`buyclaim: bonus claim grant failed for ${player.username}: tryToSet result=${result}, before=${before}, after=${after}`)
        return -1
    }
    return after
}

// Removes up to `amount` items with the given id from the inventory.
// Returns how many were actually removed.
function removeCoins(inv, id, amount) {
    let remaining = amount
    let stack = null
    for (let i = 0; i < inv.getSlots() && remaining > 0; i++) {
        stack = inv.getStackInSlot(i)
        if (!stack.isEmpty() && stack.id == id) {
            remaining -= inv.extractItem(i, remaining, false).count
        }
    }
    return amount - remaining
}

// Gives `value` spurs worth of coins, largest denominations first.
function giveCoins(player, value) {
    let left = value
    let n = 0
    for (let i = COINS.length - 1; i >= 0 && left > 0; i--) {
        n = Math.floor(left / COINS[i].value)
        if (n > 0) {
            player.give(Item.of(COINS[i].id, n))
            left -= n * COINS[i].value
        }
    }
}

ServerEvents.commandRegistry(event => {
    const { commands: Commands, arguments: Arguments } = event

    // Surfaces script errors in chat instead of brigadier's generic
    // "An unexpected error occurred" — remove once things are stable.
    function guarded(fn) {
        return ctx => {
            try {
                return fn(ctx)
            } catch (e) {
                try {
                    ctx.source.playerOrException.tell(`§c[buyclaim error] ${e}`)
                } catch (ignored) {
                }
                console.error(`buyclaim command error: ${e}`)
                return 0
            }
        }
    }

    function showInfo(player) {
        const purchased = player.persistentData.getInt(PURCHASED_KEY)
        const next = chunkPrice(purchased + 1)
        player.tell('§6=== Claim Shop ===')
        player.tell(`§eChunks purchased so far: §f${purchased}`)
        player.tell(`§eNext chunk price: §f${next} spurs §7(prices rise 2% per chunk)`)
        player.tell('§e/buyclaim <count> §7— buy claim capacity')
        player.tell('§e/buyclaim cost <count> §7— check price first')
        player.tell('§7Coins must be loose in your inventory (not in a wallet).')
        player.tell('§7Then claim chunks on the map like always.')
        return 1
    }

    function showCost(player, count) {
        if (count < 1 || count > MAX_PER_PURCHASE) {
            player.tell(`§cCount must be between 1 and ${MAX_PER_PURCHASE}.`)
            return 0
        }
        const purchased = player.persistentData.getInt(PURCHASED_KEY)
        const price = totalPrice(purchased, count)
        player.tell(`§eNext §f${count}§e chunk(s) will cost §f${price} spurs§e.`)
        return 1
    }

    function buy(player, count) {
        if (count < 1 || count > MAX_PER_PURCHASE) {
            player.tell(`§cCount must be between 1 and ${MAX_PER_PURCHASE}.`)
            return 0
        }
        const inv = player.inventory
        const purchased = player.persistentData.getInt(PURCHASED_KEY)
        const price = totalPrice(purchased, count)

        // Count loose coins per denomination.
        const held = COINS.map(c => inv.count(c.id))
        let walletTotal = 0
        for (let i = 0; i < COINS.length; i++) {
            walletTotal += held[i] * COINS[i].value
        }

        if (walletTotal < price) {
            player.tell('§cYou are too POOR to buy more land, acquire more currency.')
            player.tell(`§7Need ${price} spurs worth of coins, you carry ${walletTotal}.`)
            return 0
        }

        // Grant the capacity FIRST — if it doesn't stick, nothing is charged.
        const newBonus = grantBonusClaims(player, count)
        if (newBonus < 0) {
            player.tell('§cClaim grant failed — nothing was charged. Tell an admin to check the server log.')
            return 0
        }

        // Take smallest coins first until the price is covered. Only the last
        // denomination used can overshoot, by less than its own value.
        // Counts were taken this same tick, so the inventory can't have
        // changed since the funds check.
        const toRemove = COINS.map(() => 0)
        let removedValue = 0
        let need = 0
        let use = 0
        for (let i = 0; i < COINS.length && removedValue < price; i++) {
            need = price - removedValue
            use = Math.min(held[i], Math.ceil(need / COINS[i].value))
            toRemove[i] = use
            removedValue += use * COINS[i].value
        }
        for (let i = 0; i < COINS.length; i++) {
            if (toRemove[i] > 0) {
                removeCoins(inv, COINS[i].id, toRemove[i])
            }
        }

        // Return overshoot as change, largest denominations first.
        if (removedValue > price) {
            giveCoins(player, removedValue - price)
        }

        player.persistentData.putInt(PURCHASED_KEY, purchased + count)
        player.tell(`§aBought §f${count}§a claim chunk(s) for §f${price} spurs§a.`)
        player.tell(`§aTotal purchased: §f${purchased + count}§a (bonus claims: ${newBonus}). Claim your new land on the map!`)
        return 1
    }

    event.register(
        Commands.literal('buyclaim')
            .executes(guarded(ctx => showInfo(ctx.source.playerOrException)))
            .then(Commands.literal('cost')
                .then(Commands.argument('count', Arguments.INTEGER.create(event))
                    .executes(guarded(ctx => showCost(ctx.source.playerOrException, Arguments.INTEGER.getResult(ctx, 'count'))))))
            .then(Commands.argument('count', Arguments.INTEGER.create(event))
                .executes(guarded(ctx => buy(ctx.source.playerOrException, Arguments.INTEGER.getResult(ctx, 'count')))))
    )
})
