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

  // Planks -> Panels with Mechanical Press
  woods.forEach(wood => {
    event.recipes.create.pressing(
      `manyideas_core:panel_${wood}`,
      `minecraft:${wood}_planks`
    )
  })

  // Wooden Panel + material -> Plate with Deployer
  const plates = [
    ['manyideas_core:plate_copper', 'minecraft:copper_ingot'],
    ['manyideas_core:plate_gold', 'minecraft:gold_ingot'],
    ['manyideas_core:plate_iron', 'minecraft:iron_ingot'],
    ['manyideas_core:plate_quartz', 'minecraft:quartz']
  ]

  woods.forEach(wood => {
    plates.forEach(([output, material]) => {
      event.recipes.create.deploying(
        output,
        [
          `manyideas_core:panel_${wood}`,
          material
        ]
      ).id(`crafttomuck:deploying/${output.split(':')[1]}_from_${wood}_panel`)
    })
  })

})