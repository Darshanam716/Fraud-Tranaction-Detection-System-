from django.db import models

class TransactionPrediction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    time = models.FloatField()
    amount = models.FloatField()
    # V1-V28 PCA features
    v1 = models.FloatField()
    v2 = models.FloatField()
    v3 = models.FloatField()
    v4 = models.FloatField()
    v5 = models.FloatField()
    v6 = models.FloatField()
    v7 = models.FloatField()
    v8 = models.FloatField()
    v9 = models.FloatField()
    v10 = models.FloatField()
    v11 = models.FloatField()
    v12 = models.FloatField()
    v13 = models.FloatField()
    v14 = models.FloatField()
    v15 = models.FloatField()
    v16 = models.FloatField()
    v17 = models.FloatField()
    v18 = models.FloatField()
    v19 = models.FloatField()
    v20 = models.FloatField()
    v21 = models.FloatField()
    v22 = models.FloatField()
    v23 = models.FloatField()
    v24 = models.FloatField()
    v25 = models.FloatField()
    v26 = models.FloatField()
    v27 = models.FloatField()
    v28 = models.FloatField()
    prediction = models.IntegerField()  # 0 = Legitimate, 1 = Fraud
    confidence = models.FloatField()

    def __str__(self):
        status = "FRAUD" if self.prediction == 1 else "LEGITIMATE"
        return f"Transaction #{self.id} - {status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ['-created_at']
