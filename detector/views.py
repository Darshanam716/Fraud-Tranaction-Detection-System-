import csv
import io
import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg

from .forms import TransactionForm, CSVUploadForm
from .models import TransactionPrediction
from .ml_utils import predict_transaction


def index(request):
    """Home / dashboard view."""
    total = TransactionPrediction.objects.count()
    fraud_count = TransactionPrediction.objects.filter(prediction=1).count()
    legit_count = TransactionPrediction.objects.filter(prediction=0).count()
    recent = TransactionPrediction.objects.all()[:10]

    fraud_pct = round((fraud_count / total * 100), 1) if total > 0 else 0

    context = {
        'total': total,
        'fraud_count': fraud_count,
        'legit_count': legit_count,
        'fraud_pct': fraud_pct,
        'recent': recent,
    }
    return render(request, 'detector/index.html', context)


def predict_single(request):
    """Single transaction prediction form."""
    form = TransactionForm(request.POST or None)
    result = None

    if request.method == 'POST' and form.is_valid():
        features = form.get_feature_vector()
        result = predict_transaction(features)

        # Save to DB
        cd = form.cleaned_data
        TransactionPrediction.objects.create(
            time=cd['time'],
            amount=cd['amount'],
            **{f'v{i}': cd[f'v{i}'] for i in range(1, 29)},
            prediction=result['prediction'],
            confidence=result['confidence'],
        )

    return render(request, 'detector/predict_single.html', {'form': form, 'result': result})


def predict_bulk(request):
    """Bulk CSV upload for batch prediction."""
    form = CSVUploadForm()
    results = []
    errors = []

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                decoded = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded))
                required_cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']

                for row_num, row in enumerate(reader, start=1):
                    try:
                        features = [float(row['Time'])]
                        for i in range(1, 29):
                            features.append(float(row[f'V{i}']))
                        features.append(float(row['Amount']))

                        res = predict_transaction(features)
                        res['row'] = row_num
                        res['time'] = row['Time']
                        res['amount'] = row['Amount']
                        results.append(res)

                        TransactionPrediction.objects.create(
                            time=float(row['Time']),
                            amount=float(row['Amount']),
                            **{f'v{i}': float(row[f'V{i}']) for i in range(1, 29)},
                            prediction=res['prediction'],
                            confidence=res['confidence'],
                        )
                    except (KeyError, ValueError) as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        if len(errors) >= 5:
                            errors.append("Too many errors — stopping.")
                            break

                if results:
                    messages.success(request, f"Processed {len(results)} transactions.")
            except Exception as e:
                messages.error(request, f"Could not read file: {e}")

    fraud_in_batch = sum(1 for r in results if r['prediction'] == 1)
    return render(request, 'detector/predict_bulk.html', {
        'form': form,
        'results': results,
        'errors': errors,
        'fraud_in_batch': fraud_in_batch,
    })


def history(request):
    """View all past predictions."""
    predictions = TransactionPrediction.objects.all()
    fraud_only = request.GET.get('fraud') == '1'
    if fraud_only:
        predictions = predictions.filter(prediction=1)
    return render(request, 'detector/history.html', {
        'predictions': predictions,
        'fraud_only': fraud_only,
    })


def api_predict(request):
    """JSON API endpoint for programmatic access."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body)
        features = body.get('features', [])
        if len(features) != 30:
            return JsonResponse({'error': 'Provide exactly 30 features: [Time, V1..V28, Amount]'}, status=400)
        result = predict_transaction([float(f) for f in features])
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
