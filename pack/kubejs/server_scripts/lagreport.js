// /lag and /tets — displays server TPS and your ping.
//
// This started as a chat-word trigger (reply when someone says "lag"), but
// the server's MultiChat mod relays all chat through Redis and consumes it
// before KubeJS's chat event fires, so a command is the reliable path.

// Colored condition label for a TPS value.
function tpsCondition(tps) {
    if (tps >= 19.5) return '§a(Perfect)'
    if (tps >= 18) return '§2(Good)'
    if (tps >= 15) return '§e(Okay)'
    if (tps >= 10) return '§6(Poor)'
    return '§c(Bad)'
}

ServerEvents.commandRegistry(event => {
    const { commands: Commands } = event

    function registerLagCommand(commandName) {
        event.register(
            Commands.literal(commandName)
                .executes(ctx => {
                    // Rhino: declarations inside try/loop/if blocks throw
                    // "redeclaration of var" at runtime — keep them all up here.
                    const player = ctx.source.playerOrException
                    const server = player.server
                    let mspt = 50
                    let tps = 0
                    let ping = -1

                    try {
                        // Average tick time -> TPS, capped at 20.
                        if (typeof server.getAverageTickTimeNanos === 'function') {
                            mspt = server.getAverageTickTimeNanos() / 1000000
                        } else {
                            mspt = server.averageTickTime
                        }

                        tps = Math.min(20, 1000 / mspt)

                        // Ping: 1.20.2+ keeps latency on the connection; older on the player.
                        if (
                            player.connection &&
                            typeof player.connection.latency === 'function'
                        ) {
                            ping = player.connection.latency()
                        } else {
                            ping = player.latency
                        }

                        player.tell(
                            `§6Server TPS is §f${tps.toFixed(1)} ${tpsCondition(tps)}§6 and your ping is §f${ping}ms§6.`
                        )

                        return 1
                    } catch (e) {
                        player.tell(`§c[lag error] ${e}`)
                        console.error(`${commandName} command error: ${e}`)
                        return 0
                    }
                })
        )
    }

    registerLagCommand('lag')
    registerLagCommand('tets')
})