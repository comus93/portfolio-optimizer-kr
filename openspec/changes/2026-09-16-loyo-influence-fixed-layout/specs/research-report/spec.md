## ADDED Requirements

### Requirement: Asset-Year Influence fits the primary desktop report width
When Asset-Year Influence can remain legible at the report's normal desktop width, the table MUST use the available section width without introducing horizontal scrolling merely because generic LOYO tables prefer natural content width.

The Asset-Year Influence layout MUST keep Year compact, keep the Metric label on one line at a realistic fixed width, and distribute the remaining width across asset columns. Asset Name/Ticker identity, year-group zebra banding, and metric-specific numeric conditional backgrounds MUST remain visible.

This fixed-width rule applies to Asset-Year Influence only. LOYO Summary and Allocation Changes MAY retain their existing overflow behavior when their content needs more width.

#### Scenario: eight-asset Asset-Year Influence
- GIVEN an eight-asset LOYO report at the standard desktop report width
- WHEN Asset-Year Influence is rendered
- THEN the table fills the section width, Year and Metric retain readable single-line labels, asset columns share the remaining width, and no horizontal scrollbar is required for that matrix

#### Scenario: preserve heatmap and identity
- GIVEN fixed-width Asset-Year Influence columns
- WHEN asset headers and metric values are rendered
- THEN Name/Ticker two-line identity, Name ellipsis, year zebra banding and numeric conditional backgrounds remain intact
