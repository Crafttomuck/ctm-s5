ServerEvents.recipes(event => {
    // Remove existing limestone crushing recipe
    event.remove({ type: 'create:crushing', input: 'tfmg:limestone' })

    // Re-add with limesand included
    event.recipes.create.crushing([
        Item.of('garnished:crushed_salt'),
        Item.of('create:zinc_nugget').withChance(0.05),
        Item.of('minecraft:iron_nugget').withChance(0.1),
        Item.of('tfmg:limesand').withChance(0.5)
    ], 'tfmg:limestone')
})