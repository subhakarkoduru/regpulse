# Golden eval cases

Each case is a JSON file shaped like:

```json
{
  "name": "dti-cap-tightened",
  "old_sections": [
    {"section_id": "B3-6-02", "heading": "Debt-to-Income Ratios",
     "body": "The maximum DTI ratio is 50%."}
  ],
  "new_sections": [
    {"section_id": "B3-6-02", "heading": "Debt-to-Income Ratios",
     "body": "The maximum DTI ratio is 45%."}
  ],
  "expected_diffs": [
    {"section_id": "B3-6-02", "change_type": "modified"}
  ]
}
```

Target: ~30 historical cases over time. Week 1: first 3–5, each built from a
real bulletin change.
