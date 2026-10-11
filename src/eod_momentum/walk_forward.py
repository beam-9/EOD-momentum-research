import pandas as pd


def folds(start, holdout, *, train_months=12, validation_months=3, test_months=3):
    """Half-open intervals; complete outer windows only, no OOS overlaps."""
    counts = [train_months, validation_months, test_months]
    if any(not isinstance(n, int) or isinstance(n, bool) or n <= 0 for n in counts):
        raise ValueError('Month counts must be positive integers')
    anchor, limit = pd.Timestamp(start), pd.Timestamp(holdout)
    if anchor >= limit:
        raise ValueError('Development start must precede holdout')
    out = []
    while True:
        train_end = anchor + pd.DateOffset(months=train_months)
        val_end = train_end + pd.DateOffset(months=validation_months)
        test_end = val_end + pd.DateOffset(months=test_months)
        if test_end > limit:
            break
        out.append({'fold': len(out), 'train_start': str(anchor.date()),
                    'train_end': str(train_end.date()), 'validation_start': str(train_end.date()),
                    'validation_end': str(val_end.date()), 'test_start': str(val_end.date()),
                    'test_end': str(test_end.date())})
        anchor += pd.DateOffset(months=test_months)
    return out


def in_interval(day, start, end):
    return start <= day < end


def purge(samples, evaluation_start, evaluation_end):
    """Remove overlapping outcome windows, inclusive endpoint conservative."""
    return [s for s in samples if s['label_end_at'] < evaluation_start or
            s['label_start_at'] >= evaluation_end]
