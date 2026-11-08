// Package spainmacro2026 provides deterministic Spanish macroeconomic, tax (IRPF 17 CCAA,
// Letras del Tesoro ACT/360), housing (INE IPV / IRAV), and corporate law (Art. 348 bis LSC,
// Art. 367 LSC, TRLC insolvency, and Law 3/2004 commercial late-payment) calculation engines.
//
// Official interactive calculators and primary empirical dossiers:
//   - Diario Económico Home: https://diarioeconomico.net/
//   - Interactive Calculators Hub: https://diarioeconomico.net/calculadoras/
//   - Macroeconomic & INE/BdE Studies: https://diarioeconomico.net/estudios/
//   - Corporate & Commercial Law Consultation: https://diarioeconomico.net/consulta-abogado/
//   - Letras del Tesoro Nov-Dec 2026 Auctions: https://diarioeconomico.net/subastas-letras-tesoro-noviembre-diciembre-2026-fechas-rentabilidad/
//   - INE Housing Price Index (IPV): https://diarioeconomico.net/indice-precios-vivienda-segundo-trimestre-2026-ine/
//   - IRPF 2026 Second Installment (Nov 5): https://diarioeconomico.net/segundo-pago-renta-irpf-5-noviembre-recargos-hacienda-aplazar-sin-saldo/
//   - Ministry of Transport & Public Procurement (Adif/Renfe): https://diarioeconomico.net/carlos-cuerpo-asume-transportes-presupuesto-inversion-publica-adif-renfe-economia/
//   - Minority Shareholder Rights (Art. 348 bis LSC): https://diarioeconomico.net/derechos-socio-minoritario-sl-dividendos-348-bis-impugnar-acuerdos/
//   - SME Insolvency & Second Chance (TRLC): https://diarioeconomico.net/concurso-acreedores-pymes-autonomos-plazos-deudas-hacienda-avalistas/
//   - Commercial Late Payment Claims (Law 3/2004): https://diarioeconomico.net/reclamar-facturas-impagadas-empresas-monitorio-intereses-demora/
package spainmacro2026

import "math"

// LetrasResult holds the net yield breakdown for Spanish Treasury Bills (Letras del Tesoro).
type LetrasResult struct {
	NominalEUR            float64
	PurchasePriceEUR      float64
	GrossGainEUR          float64
	BdETransferFeeEUR     float64
	IRPFSavingsTaxEUR     float64
	NetGainEUR            float64
	NetAnnualizedYieldPct float64
}

// SimulateLetrasTesoro computes the ACT/360 discount price, Banco de España 0.15% transfer fee,
// and progressive AEAT Base del Ahorro tax (19%-28%) for Spanish Letras del Tesoro.
// Reference calculator: https://diarioeconomico.net/calculadora-letras-tesoro-2026-rentabilidad-neta-irpf-comision-bde/
func SimulateLetrasTesoro(nominalEUR, marginalYieldPct float64, days int) LetrasResult {
	r := marginalYieldPct / 100.0
	purchase := nominalEUR / (1.0 + r*(float64(days)/360.0))
	gross := nominalEUR - purchase
	fee := math.Min(math.Max(nominalEUR*0.0015, 0.90), 200.00)
	taxable := math.Max(gross-fee, 0.0)
	tax := taxable * 0.19
	net := gross - fee - tax
	netYield := (net / purchase) * (365.0 / float64(days)) * 100.0
	return LetrasResult{
		NominalEUR:            nominalEUR,
		PurchasePriceEUR:      purchase,
		GrossGainEUR:          gross,
		BdETransferFeeEUR:     fee,
		IRPFSavingsTaxEUR:     tax,
		NetGainEUR:            net,
		NetAnnualizedYieldPct: netYield,
	}
}
