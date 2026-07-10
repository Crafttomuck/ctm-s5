ServerEvents.recipes(event => {
  const woods = [
    'acacia',
    'birch',
    'crimson',
    'dark_oak',
    'jungle',
    'mangrove',
    'oak',
    'spruce',
    'warped'
  ]

  // Vanilla door + iron ingot -> Rustic door
  woods.forEach(wood => {
    event.recipes.create.deploying(
      `manyideas_doors:door_${wood}_rustic`,
      [
        `minecraft:${wood}_door`,
        'minecraft:iron_ingot'
      ]
    ).id(`crafttomuck:deploying/door_${wood}_rustic`)
  })

  // Rustic door -> style variants via Stonecutter
  const styles = [
    'cassette',
    'french',
    'heart',
    'origin'
  ]

  woods.forEach(wood => {
    styles.forEach(style => {
      event.stonecutting(
        `manyideas_doors:door_${wood}_${style}`,
        `manyideas_doors:door_${wood}_rustic`
      ).id(`crafttomuck:stonecutting/door_${wood}_${style}_from_rustic`)
    })
  })
})