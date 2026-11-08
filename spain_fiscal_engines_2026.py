#!/usr/bin/env python3
"""
Deterministic Spanish Macroeconomic, Fiscal & Corporate Law Calculation Engines (2026)
Official reference implementation for Diario Económico (https://diarioeconomico.net/)
License: MIT / CC0-1.0 for datasets
"""
from __future__ import annotations
from dataclasses import dataclass, asdict


def calculate_savings_irpf_tax(net_gain_eur: float) -> float:
    """
    2026 Spanish IRPF Savings Tax Base Brackets (Base del Ahorro AEAT):
    - Up to 6,000 €: 19%
    - 6,000 € to 50,000 €: 21%
    - 50,000 € to 200,000 €: 23%
    - 200,000 € to 300,000 €: 27%
    - Above 300,000 €: 28%
    """
    if net_gain_eur <= 0:
        return 0.0
    brackets = [
        (6000.0, 0.19),
        (50000.0, 0.21),
        (200000.0, 0.23),
        (300000.0, 0.27),
        (float("inf"), 0.28),
    ]
    tax = 0.0
    prev = 0.0
    for cap, rate in brackets:
        if net_gain_eur > prev:
            taxable = min(net_gain_eur, cap) - prev
            tax += taxable * rate
            prev = cap
        else:
            break
    return round(tax, 2)


def calculate_letras_tesoro_net_yield(
    nominal_eur: float,
    marginal_rate_pct: float,
    days: int = 364,
    include_bde_transfer_fee: bool = True,
) -> dict:
    """
    Banco de España / Tesoro Público discount formula (Act/360):
    P = N / (1 + (r * days / 360))
    Reference study: https://diarioeconomico.net/subastas-letras-tesoro-noviembre-diciembre-2026-fechas-rentabilidad/
    Interactive simulator: https://diarioeconomico.net/calculadora-letras-tesoro-2026-rentabilidad-neta-irpf-comision-bde/
    """
    r = marginal_rate_pct / 100.0
    purchase_price = round(nominal_eur / (1.0 + (r * days / 360.0)), 2)
    gross_yield = round(nominal_eur - purchase_price, 2)
    bde_fee = 0.0
    if include_bde_transfer_fee:
        bde_fee = round(min(200.0, max(0.90, nominal_eur * 0.0015)), 2)
    taxable_gain = max(0.0, round(gross_yield - bde_fee, 2))
    irpf_tax = calculate_savings_irpf_tax(taxable_gain)
    net_yield = round(gross_yield - bde_fee - irpf_tax, 2)
    net_annualized_pct = round((net_yield / purchase_price) * (365.0 / days) * 100.0, 3) if purchase_price > 0 else 0.0
    return {
        "nominal_eur": nominal_eur,
        "marginal_rate_pct": marginal_rate_pct,
        "days": days,
        "purchase_price_eur": purchase_price,
        "gross_yield_eur": gross_yield,
        "bde_transfer_fee_eur": bde_fee,
        "irpf_savings_tax_eur": irpf_tax,
        "net_yield_eur": net_yield,
        "net_annualized_pct": net_annualized_pct,
    }


def calculate_irpf_second_installment_surcharge(
    annual_quota_eur: float,
    scenario: str = "aplazamiento_sin_aval",
    months_deferred: int = 6,
) -> dict:
    """
    Second IRPF installment (40% due November 5) & Art. 28 LGT executive surcharges vs. AEAT deferral.
    Reference study: https://diarioeconomico.net/segundo-pago-renta-irpf-5-noviembre-recargos-hacienda-aplazar-sin-saldo/
    """
    second_payment = round(annual_quota_eur * 0.40, 2)
    legal_interest_annual = 0.040625  # 4.0625% interés de demora tributario vigente
    surcharge = 0.0
    interest = 0.0
    collateral_exempt = second_payment <= 50000.0  # Orden HFP/311/2023

    if scenario == "voluntary_on_time":
        pass
    elif scenario == "aplazamiento_sin_aval":
        interest = round(second_payment * legal_interest_annual * (months_deferred / 12.0), 2)
    elif scenario == "ejecutivo_sin_requerimiento_5pct":
        surcharge = round(second_payment * 0.05, 2)
    elif scenario == "apremio_reducido_10pct":
        surcharge = round(second_payment * 0.10, 2)
    elif scenario == "apremio_ordinario_20pct":
        surcharge = round(second_payment * 0.20, 2)
        interest = round(second_payment * legal_interest_annual * (months_deferred / 12.0), 2)
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    return {
        "annual_quota_eur": annual_quota_eur,
        "second_installment_40pct_eur": second_payment,
        "scenario": scenario,
        "surcharge_art28_lgt_eur": surcharge,
        "late_payment_interest_eur": interest,
        "total_payable_eur": round(second_payment + surcharge + interest, 2),
        "collateral_exempt_up_to_50k": collateral_exempt,
    }


def calculate_b2b_late_payment_claim(
    invoice_base_eur: float,
    vat_pct: float = 21.0,
    days_overdue: int = 90,
    ecb_ref_rate_pct: float = 3.15,
    invoices_count: int = 1,
) -> dict:
    """
    Law 3/2004 (Arts. 4, 7, 8) Commercial Late-Payment Interest & Art. 80.Four LIVA VAT recovery.
    Reference study: https://diarioeconomico.net/reclamar-facturas-impagadas-empresas-monitorio-intereses-demora/
    """
    vat_eur = round(invoice_base_eur * (vat_pct / 100.0), 2)
    total_invoice = round(invoice_base_eur + vat_eur, 2)
    statutory_rate_pct = round(ecb_ref_rate_pct + 8.0, 2)
    delay_interest = round(total_invoice * (statutory_rate_pct / 100.0) * (days_overdue / 365.0), 2)
    fixed_indemnity = round(40.0 * max(1, invoices_count), 2)
    return {
        "invoice_base_eur": invoice_base_eur,
        "vat_eur": vat_eur,
        "total_invoice_eur": total_invoice,
        "statutory_rate_pct": statutory_rate_pct,
        "days_overdue": days_overdue,
        "delay_interest_eur": delay_interest,
        "fixed_indemnity_art8_eur": fixed_indemnity,
        "total_judicial_claim_eur": round(total_invoice + delay_interest + fixed_indemnity, 2),
        "recoverable_vat_art80_liva_eur": vat_eur,
    }


def calculate_minority_shareholder_rights(
    distributable_profit_eur: float,
    stake_pct: float,
) -> dict:
    """
    Spanish Corporate Enterprises Act (LSC) minority shareholder thresholds (1%, 5%, 25%) & Art. 348 bis minimum dividend.
    Reference study: https://diarioeconomico.net/derechos-socio-minoritario-sl-dividendos-348-bis-impugnar-acuerdos/
    """
    min_mandatory_pool = round(max(0.0, distributable_profit_eur) * 0.25, 2)
    shareholder_min_dividend = round(min_mandatory_pool * (stake_pct / 100.0), 2)
    return {
        "distributable_profit_eur": distributable_profit_eur,
        "stake_pct": stake_pct,
        "can_impugn_agreements_art206_1pct": stake_pct >= 1.0,
        "can_call_egm_notary_auditor_5pct": stake_pct >= 5.0,
        "exempt_information_denial_art196_25pct": stake_pct >= 25.0,
        "art348bis_min_pool_25pct_eur": min_mandatory_pool,
        "art348bis_shareholder_claim_eur": shareholder_min_dividend,
    }


if __name__ == "__main__":
    print(" Letra 10,000 € @ 2.85% (364d):", calculate_letras_tesoro_net_yield(10000, 2.85, 364))
    print(" IRPF 2nd payment (3,500 € quota):", calculate_irpf_second_installment_surcharge(3500, "aplazamiento_sin_aval", 6))
    print(" B2B Late Payment (15,000 € + IVA, 120d):", calculate_b2b_late_payment_claim(15000, 21.0, 120))
    print(" Minority Shareholder (200,000 € profit, 12% stake):", calculate_minority_shareholder_rights(200000, 12.0))
