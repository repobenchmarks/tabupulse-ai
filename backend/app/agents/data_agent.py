import io
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

class DataAgent:
    """
    Autonomous Tabular Data Agent.
    Inspects schemas, detects target variables, preprocesses tabular features,
    and formats them optimally for TabPFN inference.
    """

    def __init__(self):
        pass

    def load_csv(self, file_content: str | bytes) -> pd.DataFrame:
        if isinstance(file_content, bytes):
            return pd.read_csv(io.BytesIO(file_content))
        return pd.read_csv(io.StringIO(file_content))

    def inspect_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Inspect dataset columns, types, null counts, and suggest target column.
        """
        columns_info = []
        possible_targets = []

        total_rows = len(df)
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())
            sample_values = df[col].dropna().head(3).tolist()

            is_id = False
            col_lower = col.lower()
            if "id" in col_lower or "guid" in col_lower or "uuid" in col_lower:
                if unique_count > total_rows * 0.8:
                    is_id = True

            col_meta = {
                "name": col,
                "dtype": dtype,
                "null_count": null_count,
                "unique_count": unique_count,
                "sample_values": sample_values,
                "is_id_column": is_id
            }
            columns_info.append(col_meta)

            # Heuristics for target prediction
            if not is_id:
                target_score = 0
                if any(kw in col_lower for kw in ["churn", "target", "label", "paid", "late", "convert", "risk", "status"]):
                    target_score += 10
                if unique_count == 2:
                    target_score += 5
                elif 2 < unique_count <= 10:
                    target_score += 2

                if target_score > 0:
                    possible_targets.append({
                        "column": col,
                        "score": target_score,
                        "type": "classification" if unique_count <= 10 else "regression"
                    })

        possible_targets.sort(key=lambda x: x["score"], reverse=True)
        recommended_target = possible_targets[0]["column"] if possible_targets else df.columns[-1]

        return {
            "total_rows": total_rows,
            "total_columns": len(df.columns),
            "columns": columns_info,
            "recommended_target": recommended_target,
            "candidate_targets": possible_targets,
            "preview_rows": df.head(10).to_dict(orient="records")
        }

    def prepare_data_for_tabpfn(
        self,
        df: pd.DataFrame,
        target_col: str,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Preprocesses tabular data for TabPFN:
        - Drops pure ID/name columns
        - Encodes categorical variables
        - Handles missing values
        - Splits into train and test sets
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset")

        df_clean = df.copy()

        # Identify ID columns to exclude
        exclude_cols = [target_col]
        for col in df_clean.columns:
            col_lower = col.lower()
            if col != target_col:
                if ("id" in col_lower or "uuid" in col_lower) and df_clean[col].nunique() > len(df_clean) * 0.7:
                    exclude_cols.append(col)

        feature_cols = [c for c in df_clean.columns if c not in exclude_cols]

        y_raw = df_clean[target_col]

        # Determine task type
        unique_targets = y_raw.nunique()
        is_classification = unique_targets <= 10 and (
            y_raw.dtype == "object" or y_raw.dtype == "bool" or pd.api.types.is_integer_dtype(y_raw.dtype)
        )
        task_type = "classification" if is_classification else "regression"

        # Encode target if classification
        if is_classification:
            target_mapping = {}
            if y_raw.dtype == "object" or y_raw.dtype == "bool":
                unique_vals = sorted(y_raw.dropna().unique())
                target_mapping = {val: idx for idx, val in enumerate(unique_vals)}
                y = y_raw.map(target_mapping).values
            else:
                y = y_raw.values
        else:
            target_mapping = {}
            y = y_raw.astype(float).values

        # Feature preprocessing: one-hot or numeric
        X_df = df_clean[feature_cols].copy()
        for col in feature_cols:
            if X_df[col].dtype == "object":
                X_df[col] = X_df[col].astype("category").cat.codes
            elif X_df[col].isnull().any():
                X_df[col] = X_df[col].fillna(X_df[col].median())

        X = X_df.values

        # Split train/test
        from sklearn.model_selection import train_test_split
        stratify = y if is_classification and len(np.unique(y)) > 1 and min(pd.Series(y).value_counts()) >= 2 else None

        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
            X, y, df_clean.index.values,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify
        )

        return {
            "task_type": task_type,
            "feature_names": feature_cols,
            "target_col": target_col,
            "target_mapping": target_mapping,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "test_original_df": df_clean.iloc[indices_test].to_dict(orient="records"),
            "train_size": len(X_train),
            "test_size": len(X_test)
        }
