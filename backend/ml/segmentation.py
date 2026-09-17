import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


REQUIRED_COLUMNS = [
    "Age",
    "Income",
    "Purchase_Frequency",
    "Average_Spend",
    "Website_Visits",
    "Email_Engagement",
]


def segment_customers(rows, n_clusters=3):
    """
    Segment customers using K-Means clustering.

    rows:
        List of customer dictionaries.

    Returns:
        segmented_customers, segment_summaries
    """

    if not rows:
        raise ValueError("No customer records were provided.")

    # Check required columns.
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in rows[0]
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    valid_customers = []

    for row in rows:
        try:
            customer = {
                "Customer_ID": row.get("Customer_ID", "").strip(),
                "Age": float(row["Age"]),
                "Income": float(row["Income"]),
                "Purchase_Frequency": float(
                    row["Purchase_Frequency"]
                ),
                "Average_Spend": float(
                    row["Average_Spend"]
                ),
                "Website_Visits": float(
                    row["Website_Visits"]
                ),
                "Email_Engagement": float(
                    row["Email_Engagement"]
                ),
            }

            valid_customers.append(customer)

        except (ValueError, TypeError, KeyError):
            # Ignore invalid rows instead of crashing the entire upload.
            continue

    if len(valid_customers) < n_clusters:
        raise ValueError(
            f"At least {n_clusters} valid customers are required."
        )

    # Convert numerical customer features into a NumPy matrix.
    feature_matrix = np.array([
        [
            customer["Age"],
            customer["Income"],
            customer["Purchase_Frequency"],
            customer["Average_Spend"],
            customer["Website_Visits"],
            customer["Email_Engagement"],
        ]
        for customer in valid_customers
    ])

    # Standardize values so large-scale variables do not dominate.
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_matrix)

    # K-Means clustering.
    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    cluster_labels = model.fit_predict(scaled_features)

    # Attach segment numbers to customers.
    segmented_customers = []

    for customer, label in zip(valid_customers, cluster_labels):
        customer_copy = customer.copy()
        customer_copy["Segment"] = int(label)
        segmented_customers.append(customer_copy)

    # Build segment summaries.
    segment_summaries = []

    for segment_id in sorted(set(cluster_labels)):
        segment_customers = [
            customer
            for customer in segmented_customers
            if customer["Segment"] == int(segment_id)
        ]

        def average(field):
            return round(
                sum(customer[field] for customer in segment_customers)
                / len(segment_customers),
                2
            )

        segment_summaries.append({
            "segment_id": int(segment_id),
            "customer_count": len(segment_customers),
            "average_age": average("Age"),
            "average_income": average("Income"),
            "average_purchase_frequency": average(
                "Purchase_Frequency"
            ),
            "average_spend": average("Average_Spend"),
            "average_website_visits": average(
                "Website_Visits"
            ),
            "average_email_engagement": average(
                "Email_Engagement"
            ),
        })

    return segmented_customers, segment_summaries