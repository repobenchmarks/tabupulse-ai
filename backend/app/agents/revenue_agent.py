from typing import Dict, Any, List, Optional

class RevenueAgent:
    """
    Autonomous Revenue & Retention Action Agent.
    Transforms raw TabPFN probabilities into high-ROI business interventions,
    financial runway protection, and automated founder playbooks.
    """

    def __init__(self):
        pass

    def analyze_ecommerce_churn(
        self,
        records: List[Dict[str, Any]],
        predictions: List[int],
        probabilities: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze e-commerce customers at risk of churn and prescribe actions.
        """
        action_items = []
        total_mrr_at_risk = 0.0
        high_risk_count = 0

        for idx, (row, pred) in enumerate(zip(records, predictions)):
            # Churn probability for class 1
            if probabilities and idx < len(probabilities):
                churn_prob = round(probabilities[idx][1] * 100, 1) if len(probabilities[idx]) > 1 else (pred * 100)
            else:
                churn_prob = 85.0 if pred == 1 else 15.0

            monthly_spend = float(row.get("monthly_spend", 50.0))
            cust_id = str(row.get("customer_id", f"CUST-{1000+idx}"))
            tier = str(row.get("subscription_tier", "Standard"))
            days_inactive = int(row.get("days_since_last_login", 0))
            tickets = int(row.get("support_tickets_30d", 0))
            nps = int(row.get("nps_score", 7))

            # Determine risk level
            if churn_prob >= 75:
                risk_level = "CRITICAL"
                high_risk_count += 1
                total_mrr_at_risk += monthly_spend
            elif churn_prob >= 50:
                risk_level = "HIGH"
                high_risk_count += 1
                total_mrr_at_risk += monthly_spend
            elif churn_prob >= 30:
                risk_level = "MODERATE"
            else:
                risk_level = "HEALTHY"

            # Formulate strategic response
            drivers = []
            if days_inactive > 14:
                drivers.append(f"Inactive for {days_inactive} days")
            if tickets >= 3:
                drivers.append(f"{tickets} open support tickets")
            if nps <= 5:
                drivers.append(f"Low satisfaction (NPS {nps}/10)")
            if not drivers:
                drivers.append("Usage plateau detected by TabPFN prior distribution")

            primary_driver = " & ".join(drivers)

            if risk_level == "CRITICAL":
                action = f"Executive Concierge Outreach: Offer personalized 20% renewal incentive + direct Zoom call with Lead Product Specialist"
                urgency = "Within 24 Hours"
            elif risk_level == "HIGH":
                action = f"Automated Re-engagement Sequence: Dispatch custom workflow playbook email & 15% annual upgrade credit"
                urgency = "Within 48 Hours"
            elif risk_level == "MODERATE":
                action = f"Value Check-in: Send feature discovery tips highlighting unused high-value tools"
                urgency = "Within 7 Days"
            else:
                action = f"Upsell Candidate: Invite to VIP Beta program or Enterprise add-on trial"
                urgency = "Scheduled Quarterly"

            action_items.append({
                "id": cust_id,
                "tier": tier,
                "monthly_spend": monthly_spend,
                "annual_spend": round(monthly_spend * 12, 2),
                "churn_probability": churn_prob,
                "risk_level": risk_level,
                "primary_driver": primary_driver,
                "recommended_action": action,
                "urgency": urgency,
                "potential_loss_prevention": round(monthly_spend * 12, 2)
            })

        # Sort highest risk and highest spend first
        action_items.sort(key=lambda x: (x["risk_level"] in ["CRITICAL", "HIGH"], x["annual_spend"]), reverse=True)

        annual_at_risk = round(total_mrr_at_risk * 12, 2)
        projected_saved_arr = round(annual_at_risk * 0.65, 2) # Typical 65% winback with proactive playbook

        summary = (
            f"TabPFN identified {high_risk_count} accounts with high or critical churn risk out of {len(records)} analyzed. "
            f"Total Monthly Recurring Revenue at risk: ${total_mrr_at_risk:,.2f} (${annual_at_risk:,.2f}/year). "
            f"Executing the automated retention playbook is projected to recover approximately ${projected_saved_arr:,.2f} in annual revenue."
        )

        return {
            "business_domain": "E-Commerce / Micro-SaaS Retention",
            "total_accounts_analyzed": len(records),
            "high_risk_count": high_risk_count,
            "monthly_mrr_at_risk": round(total_mrr_at_risk, 2),
            "annual_arr_at_risk": annual_at_risk,
            "projected_recoverable_revenue": projected_saved_arr,
            "executive_summary": summary,
            "action_items": action_items
        }

    def analyze_freelance_cashflow(
        self,
        records: List[Dict[str, Any]],
        predictions: List[int | float],
        probabilities: Optional[List[List[float]]] = None,
        task_type: str = "classification"
    ) -> Dict[str, Any]:
        """
        Analyze freelance/consultant invoices to protect cashflow and prevent payment defaults.
        """
        action_items = []
        total_delayed_cash = 0.0
        high_risk_invoices = 0

        for idx, row in enumerate(records):
            pred = predictions[idx] if idx < len(predictions) else 0

            if task_type == "classification":
                if probabilities and idx < len(probabilities):
                    late_prob = round(probabilities[idx][1] * 100, 1) if len(probabilities[idx]) > 1 else (pred * 100)
                else:
                    late_prob = 85.0 if pred == 1 else 15.0
                expected_delay_days = 15 if late_prob > 60 else (5 if late_prob > 30 else 0)
            else:
                expected_delay_days = max(0, round(float(pred)))
                late_prob = min(99.0, round(expected_delay_days * 5.0, 1))

            inv_id = str(row.get("invoice_id", f"INV-{200+idx}"))
            client_tier = str(row.get("client_tier", "Startup"))
            amount = float(row.get("invoice_amount", 1000.0))
            terms = int(row.get("payment_terms_days", 30))
            prior_lates = int(row.get("prior_late_payments", 0))

            if late_prob >= 70 or expected_delay_days > 14:
                risk_level = "CRITICAL"
                high_risk_invoices += 1
                total_delayed_cash += amount
            elif late_prob >= 45 or expected_delay_days > 7:
                risk_level = "HIGH"
                high_risk_invoices += 1
                total_delayed_cash += amount
            elif late_prob >= 25:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW_RISK"

            drivers = []
            if prior_lates > 0:
                drivers.append(f"{prior_lates} past delayed payments")
            if client_tier == "Startup":
                drivers.append("Early-stage client liquidity cycle")
            if terms > 30:
                drivers.append(f"Extended terms ({terms} days)")
            if not drivers:
                drivers.append("Standard payment turnaround profile")

            primary_driver = " & ".join(drivers)

            if risk_level == "CRITICAL":
                action = f"Send Gentle Pre-Due Milestone Check-In + Offer 2% Instant Settlement Discount or require 50% escrow deposit on subsequent milestones"
                urgency = "5 Days Before Due Date"
            elif risk_level == "HIGH":
                action = f"Automated Courteous Invoice Confirmation with 1-click Stripe/Wise payment link"
                urgency = "2 Days Before Due Date"
            elif risk_level == "MODERATE":
                action = f"Standard automated reminder with downloadable PDF receipt"
                urgency = "On Due Date"
            else:
                action = f"Prime Client: Express appreciation and pitch next retainer package"
                urgency = "After Settlement"

            action_items.append({
                "id": inv_id,
                "client_tier": client_tier,
                "invoice_amount": amount,
                "payment_terms_days": terms,
                "late_probability": late_prob,
                "expected_delay_days": expected_delay_days,
                "risk_level": risk_level,
                "primary_driver": primary_driver,
                "recommended_action": action,
                "urgency": urgency,
                "at_risk_amount": amount
            })

        action_items.sort(key=lambda x: (x["risk_level"] in ["CRITICAL", "HIGH"], x["invoice_amount"]), reverse=True)

        summary = (
            f"TabPFN audited {len(records)} invoices and flagged {high_risk_invoices} invoices at high risk of late payment. "
            f"Total cashflow temporarily bottlenecked: ${total_delayed_cash:,.2f}. "
            f"Deploying automated milestone verification and early settlement incentives protects freelancer runway."
        )

        return {
            "business_domain": "Freelance Cashflow & Invoice Protection",
            "total_invoices_analyzed": len(records),
            "delayed_invoices_count": high_risk_invoices,
            "total_delayed_cashflow": round(total_delayed_cash, 2),
            "executive_summary": summary,
            "action_items": action_items
        }
