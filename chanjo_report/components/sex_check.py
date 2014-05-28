# -*- coding: utf-8 -*-
"""
### Sex check

Depending on the coverage of X and Y chromosomes, a simple still very accurate
sex prediction can be made on the samples. This is a simple control step that
will yield a warning that samples can have been mixed upstream.
"""


def _group_by_sample(result_list):
  samples = {}
  for row in result_list:
    if row[0] not in samples:
      samples[row[0]] = {'X': None, 'Y': None}

    # Put coverage [2] under contig [1] under sample [0]
    samples[row[0]][row[1]] = row[2]

  return samples


def predict_sex(x_coverage, y_coverage):
  sex = 'female'
  if (y_coverage > 0) and (x_coverage / y_coverage < 10):
    sex = 'male'

  return sex


def index(db, group_id=None, sample_ids=None):
  if sample_ids:
    # Optionally limit by a list of samples
    query = db.sex_chromosome_coverage(samples=sample_ids)

  elif group_id:
    # ... or limit to a group of samples
    query = db.sex_chromosome_coverage(group=group_id)

  else:
    # Include all samples
    query = db.sex_chromosome_coverage()

  # Let's assemble the final results
  samples = _group_by_sample(query.all())
  results = []
  for sample_id, chromosomes in samples.items():
    # Predict sex from X and Y chromosome coverage
    x_coverage = chromosomes['X']
    y_coverage = chromosomes['Y']
    sex_prediction = predict_sex(x_coverage, y_coverage)

    # Combine table row
    results.append((sample_id, round(x_coverage, 2), round(y_coverage, 2),
                    sex_prediction))

  return results, __doc__
