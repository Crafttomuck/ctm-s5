// Bulk-dye planks: splash any vanilla plank into ManyIdeas red colored planks.
// ManyIdeas colored planks are a single item carrying a manyideas_core:color
// component, so the output needs the component, not a per-color item id.
// (Rewritten: the original used Utils.getRegistry, which this KubeJS build
// doesn't have, and targeted manyideas_core:red_planks, which never existed.)
ServerEvents.recipes(event => {
    const RED_PLANKS = Item.of('manyideas_core:planks_colored', '[manyideas_core:color=red]')

    Ingredient.of('#minecraft:planks').itemIds.forEach(id => {
        event.recipes.create.splashing([RED_PLANKS], [id])
            .id(`crafttomuck:splashing/red_planks_from_${id.replace(':', '_')}`)
    })
})
