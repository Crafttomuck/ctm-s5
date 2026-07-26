// Fix for TFMG 1.2.2 chemical vat liquid concrete recipe.
//
// The stock recipe (tfmg:vat_machine_recipe/concrete) outputs 32000mb of
// liquid concrete, but VatBlockEntity.getMatchingRecipe() hard-rejects any
// recipe whose total fluid output exceeds 4000mb (the per-tank base size),
// regardless of actual vat capacity. The recipe can therefore never match
// and the vat silently does nothing. Upstream bug in the mod itself.
//
// Workaround: replace the recipe with an identical one capped at 4000mb.
// Note: the vat only re-runs the recipe once the output tank is drained
// below 1mb of liquid concrete, so keep a pump pulling concrete out.
ServerEvents.recipes(event => {
  event.remove({ id: 'tfmg:vat_machine_recipe/concrete' })
  // older-style id, in case the recipe loader flattens the path differently
  event.remove({ id: 'tfmg:concrete' })

  event.custom({
    type: 'tfmg:vat_machine_recipe',
    allowed_vat_types: [
      'tfmg:cast_iron_vat',
      'tfmg:steel_vat',
      'tfmg:firebrick_lined_vat'
    ],
    ingredients: [
      { item: 'minecraft:sand' },
      { item: 'minecraft:gravel' },
      { item: 'tfmg:limesand' },
      { type: 'neoforge:single', amount: 250, fluid: 'minecraft:water' }
    ],
    machines: ['tfmg:mixing'],
    min_size: 1,
    results: [
      { amount: 4000, id: 'tfmg:liquid_concrete' }
    ]
  }).id('crafttomuck:vat/liquid_concrete_fixed')
})
