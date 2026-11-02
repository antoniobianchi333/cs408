# Lab 2 grading (TA only)

Not distributed. It holds the hidden checkpoints and the one evaluation that
uses them.

```bash
source skeleton/scripts/activate.sh
python grading/eval.py --alias A --tasks paperless dateutil ...
```

`eval.py` re-evaluates `skeleton/jobs/<alias>/<id>/` in a fresh environment with
all checkpoints (issue reproduction: with the task's reference repair,
`skeleton/tasks/issue-reproduction/<id>/solution.patch`). It writes
`eval-full.json` (score plus `public_score` and `hidden_score`) next to the
job's `eval.json`, and never changes `eval.json`. The alias `submission` resolves
to `skeleton/jobs/submission/<type>/<id>/`. Errors print `error: ...` and the
exit status is 2.

```
tasks/<type>/<id>/checkpoints.json   all checkpoints, public and hidden ("hidden": true),
                                     with every faulty version
```

The public checkpoints in `skeleton/tasks/<type>/<id>/checkpoints.json` are the
entries here without `"hidden": true`.
