"""
Dummy policy / FAQ data used by the Policy Retrieval Node.
Maps banking intents to relevant policy snippets, typical resolutions,
and escalation requirements.

In production this would query a real database; here we use a static dictionary.
"""

POLICIES: dict = {
    # ── Card Issues ─────────────────────────────────────────────
    "card_not_received": {
        "title": "Card Not Received Policy",
        "policy_text": (
            "If a customer has not received their card within 10 business days "
            "of the request, they should first verify their mailing address. "
            "The bank can issue a replacement card free of charge within the "
            "first 30 days. After 30 days, a reissue fee of $15 may apply."
        ),
        "typical_resolution": (
            "Verify address → Cancel old card → Issue replacement → "
            "Provide tracking number"
        ),
        "escalation_required": False,
    },
    "activate_my_card": {
        "title": "Card Activation Policy",
        "policy_text": (
            "Customers can activate their new card via the mobile app, "
            "online banking portal, or by calling the activation hotline. "
            "The card must be activated within 60 days of issuance."
        ),
        "typical_resolution": (
            "Guide customer through app/web activation steps or "
            "transfer to automated phone activation"
        ),
        "escalation_required": False,
    },
    "lost_or_stolen_card": {
        "title": "Lost or Stolen Card Policy",
        "policy_text": (
            "Immediately block the card to prevent unauthorized transactions. "
            "Issue a replacement card via expedited delivery (2-3 business days). "
            "Review recent transactions for any unauthorized activity and "
            "initiate a dispute if necessary."
        ),
        "typical_resolution": (
            "Block card immediately → Review transactions → "
            "Issue replacement → File dispute if needed"
        ),
        "escalation_required": True,
    },
    "card_payment_not_recognised": {
        "title": "Unrecognized Card Payment Policy",
        "policy_text": (
            "If a customer does not recognize a transaction, verify the merchant "
            "name and date. Some transactions may appear with different merchant "
            "names. If confirmed unauthorized, initiate a chargeback process. "
            "Temporary credit may be issued within 5 business days."
        ),
        "typical_resolution": (
            "Verify transaction details → Block card if fraud suspected → "
            "Initiate chargeback → Issue temporary credit"
        ),
        "escalation_required": True,
    },

    # ── Transfer Issues ─────────────────────────────────────────
    "transfer_not_received_by_recipient": {
        "title": "Transfer Not Received Policy",
        "policy_text": (
            "Transfers between banks may take 1-3 business days. "
            "If the recipient has not received funds after 3 business days, "
            "verify the recipient's account details. The bank can initiate "
            "a trace on the transfer. International transfers may take up to "
            "5 business days."
        ),
        "typical_resolution": (
            "Verify recipient details → Check transfer status → "
            "Initiate trace if needed → Provide timeline"
        ),
        "escalation_required": False,
    },
    "failed_transfer": {
        "title": "Failed Transfer Policy",
        "policy_text": (
            "If a transfer fails, the funds are typically returned to the "
            "sender's account within 1-2 business days. Common causes include "
            "incorrect account details, insufficient funds, or bank maintenance. "
            "No additional fee is charged for failed transfers."
        ),
        "typical_resolution": (
            "Identify failure reason → Confirm refund timeline → "
            "Help retry with correct details"
        ),
        "escalation_required": False,
    },

    # ── Account Issues ──────────────────────────────────────────
    "blocked_account": {
        "title": "Blocked Account Policy",
        "policy_text": (
            "Accounts may be blocked due to suspicious activity, failed login "
            "attempts, or regulatory compliance checks. The customer must verify "
            "their identity through two-factor authentication or by visiting a "
            "branch with valid ID. Unblocking typically takes 24-48 hours."
        ),
        "typical_resolution": (
            "Verify customer identity → Review block reason → "
            "Submit unblock request → Follow up in 24-48 hours"
        ),
        "escalation_required": True,
    },
    "compromised_card": {
        "title": "Compromised Card Policy",
        "policy_text": (
            "If a card is compromised, immediately freeze the card and all "
            "associated accounts. Conduct a full transaction review for the "
            "past 90 days. Issue a new card with a new number. Report the "
            "incident to the fraud department for investigation."
        ),
        "typical_resolution": (
            "Freeze card → Full transaction audit → Issue new card → "
            "Report to fraud team"
        ),
        "escalation_required": True,
    },

    # ── Refund / Dispute ────────────────────────────────────────
    "request_refund": {
        "title": "Refund Request Policy",
        "policy_text": (
            "Refunds are processed within 5-10 business days depending on "
            "the merchant and payment method. The customer should first "
            "contact the merchant directly. If the merchant refuses, the bank "
            "can initiate a chargeback for credit/debit card transactions."
        ),
        "typical_resolution": (
            "Advise contacting merchant first → If unsuccessful, initiate "
            "chargeback → Provide timeline for refund"
        ),
        "escalation_required": False,
    },

    # ── Top-up / Balance ────────────────────────────────────────
    "top_up_failed": {
        "title": "Top-Up Failed Policy",
        "policy_text": (
            "If a top-up fails, the debited amount should be refunded within "
            "24 hours. Common causes include network issues, card verification "
            "failure, or exceeding daily limits. If funds were deducted but not "
            "credited, submit a manual reversal request."
        ),
        "typical_resolution": (
            "Check transaction status → Verify limits → "
            "Process manual reversal if needed"
        ),
        "escalation_required": False,
    },
    "balance_not_updated_after_bank_transfer": {
        "title": "Balance Update Delay Policy",
        "policy_text": (
            "Balance updates after bank transfers may take 1-3 business days. "
            "Real-time transfers (instant payments) should reflect immediately. "
            "If the balance has not updated after 3 days, a manual reconciliation "
            "may be required."
        ),
        "typical_resolution": (
            "Verify transfer type → Check processing timeline → "
            "Initiate manual reconciliation if delayed"
        ),
        "escalation_required": False,
    },

    # ── Exchange / Fees ─────────────────────────────────────────
    "exchange_rate": {
        "title": "Exchange Rate Inquiry Policy",
        "policy_text": (
            "Exchange rates are updated every 15 minutes during market hours. "
            "The rate applied to a transaction is the rate at the time of processing, "
            "not at the time of initiation. A foreign exchange fee of 1-3% may apply."
        ),
        "typical_resolution": (
            "Provide current exchange rate → Explain fee structure → "
            "Show historical rates if requested"
        ),
        "escalation_required": False,
    },

    # ── ATM Issues ──────────────────────────────────────────────
    "atm_support": {
        "title": "ATM Support Policy",
        "policy_text": (
            "For ATM-related issues such as card retention, failed withdrawals, "
            "or incorrect dispensing, the customer should note the ATM location "
            "and time. Investigation takes 5-7 business days. Funds for failed "
            "withdrawals are typically reversed within 24 hours."
        ),
        "typical_resolution": (
            "Collect ATM details → Log incident → "
            "Process reversal for failed withdrawal → Investigate"
        ),
        "escalation_required": False,
    },
}

# Default policy for intents not explicitly covered
DEFAULT_POLICY = {
    "title": "General Customer Support Policy",
    "policy_text": (
        "Thank you for contacting our support team. Our representatives "
        "are available to assist you with any banking-related inquiries. "
        "Please provide as much detail as possible about your issue so we "
        "can help you effectively."
    ),
    "typical_resolution": (
        "Gather customer details → Identify the issue category → "
        "Provide relevant information or escalate to specialist team"
    ),
    "escalation_required": False,
}


def get_policy(intent: str) -> dict:
    """
    Retrieve the policy entry for the given intent.
    Falls back to DEFAULT_POLICY if the intent is not found.
    """
    return POLICIES.get(intent, DEFAULT_POLICY)
