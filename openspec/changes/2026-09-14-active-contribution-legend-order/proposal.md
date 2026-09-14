# Change: Align Cumulative Active Return legend with rendered stack

## Why
The Cumulative Active Return chart uses positive and negative stacked contributions, while the legend followed asset input order. This can make the legend order disagree with the visible stack and cause users to misidentify contribution segments.

## What changes
- Keep contribution calculations unchanged.
- Order the legend by the latest rendered stack from top to bottom.
- Preserve each asset's existing color identity.
