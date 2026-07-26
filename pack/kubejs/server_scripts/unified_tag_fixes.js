// Almost Unified replaces items in recipes but not in mod-specific tags that
// gameplay code checks directly. Copper nuggets unify to minecraft:copper_nugget
// (Vanilla Backport wins over create:copper_nugget), but Power Grid's circuit
// design table accepts items via #powergrid:circuit_component, which only lists
// the Create nugget. Add the unified nugget so players can actually use it.
ServerEvents.tags('item', event => {
    event.add('powergrid:circuit_component', 'minecraft:copper_nugget')
})
