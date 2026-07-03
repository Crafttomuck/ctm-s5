ServerEvents.recipes(event => {
    event.remove({ output: 'farm_and_charm:feeding_trough' })
    event.remove({ output: 'farm_and_charm:water_trough' })
})
