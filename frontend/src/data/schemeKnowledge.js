/**
 * Curated Factual Knowledge Base (38 Atomic Chunks & Metadata) for HDFC Mutual Fund Schemes.
 * Sourced directly from verified Groww factsheets (Updated: 2026-08-30).
 */

export const SUPPORTED_SCHEMES = {
  "hdfc-mid-cap-fund-direct-growth": {
    code: "hdfc-mid-cap-fund-direct-growth",
    name: "HDFC Mid-Cap Opportunities Fund",
    category: "Equity: Mid Cap",
    riskometer: "Very High",
    benchmark_index: "NIFTY Midcap 150 TRI",
    ter: "0.74%",
    source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    aliases: [
      "hdfc mid-cap opportunities fund",
      "hdfc mid cap opportunities fund",
      "hdfc mid-cap opportunities",
      "hdfc mid cap opportunities",
      "hdfc mid-cap fund",
      "hdfc mid cap fund",
      "hdfc mid-cap",
      "hdfc mid cap",
      "hdfc midcap",
      "mid-cap opportunities fund",
      "mid cap opportunities fund",
      "mid cap fund",
      "mid-cap fund",
      "mid cap",
      "midcap",
      "mid-cap"
    ]
  },
  "hdfc-small-cap-fund-direct-growth": {
    code: "hdfc-small-cap-fund-direct-growth",
    name: "HDFC Small Cap Fund",
    category: "Equity: Small Cap",
    riskometer: "Very High",
    benchmark_index: "BSE 250 SmallCap TRI",
    ter: "0.68%",
    source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    aliases: [
      "hdfc small cap fund",
      "hdfc small-cap fund",
      "hdfc small cap",
      "hdfc small-cap",
      "hdfc smallcap",
      "small cap fund",
      "small-cap fund",
      "small cap",
      "smallcap",
      "small-cap"
    ]
  },
  "hdfc-large-cap-fund-direct-growth": {
    code: "hdfc-large-cap-fund-direct-growth",
    name: "HDFC Top 100 / Large Cap Fund",
    category: "Equity: Large Cap",
    riskometer: "Very High",
    benchmark_index: "NIFTY 100 TRI",
    ter: "1.08%",
    source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    aliases: [
      "hdfc top 100 / large cap fund",
      "hdfc top 100 fund",
      "hdfc top 100",
      "hdfc top100 fund",
      "hdfc top100",
      "hdfc large cap fund",
      "hdfc large-cap fund",
      "hdfc large cap",
      "hdfc large-cap",
      "hdfc largecap",
      "top 100 fund",
      "top 100",
      "top100",
      "large cap fund",
      "large-cap fund",
      "large cap",
      "largecap",
      "large-cap"
    ]
  },
  "hdfc-elss-tax-saver-fund-direct-plan-growth": {
    code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    name: "HDFC ELSS Tax Saver Fund",
    category: "Equity: ELSS / Tax Saver",
    riskometer: "Very High",
    benchmark_index: "NIFTY 500 TRI",
    ter: "1.09%",
    source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    aliases: [
      "hdfc elss tax saver fund",
      "hdfc elss tax saver",
      "hdfc elss fund",
      "hdfc elss",
      "hdfc tax saver fund",
      "hdfc tax saver",
      "hdfc tax sevar",
      "elss tax saver fund",
      "elss tax saver",
      "elss tax sevar",
      "tax saver fund",
      "tax saver",
      "tax sevar",
      "elss fund",
      "elss"
    ]
  },
  "hdfc-gold-etf-fund-of-fund-direct-plan-growth": {
    code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    name: "HDFC Gold ETF Fund of Fund",
    category: "Commodities: Gold / Fund of Funds",
    riskometer: "High",
    benchmark_index: "Domestic Price of Physical Gold",
    ter: "0.25%",
    source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    aliases: [
      "hdfc gold etf fund of fund",
      "hdfc gold etf fof",
      "hdfc gold etf fund",
      "hdfc gold etf",
      "hdfc gold fof",
      "hdfc gold fund of fund",
      "hdfc gold fund",
      "hdfc gold",
      "gold etf fund of fund",
      "gold etf fof",
      "gold etf fund",
      "gold fof",
      "gold etf",
      "gold fund"
    ]
  }
};

export const COMPETITOR_AMCS = [
  "sbi",
  "icici",
  "icici prudential",
  "axis",
  "nippon",
  "nippon india",
  "parag parikh",
  "ppfas",
  "mirae",
  "mirae asset",
  "kotak",
  "tata",
  "dsp",
  "quant",
  "uti",
  "motilal oswal",
  "canara robeco",
  "bandhan",
  "invesco",
  "franklin",
  "franklin templeton",
  "edelweiss",
  "hsbc",
  "sundaram",
  "baroda bnp",
  "pgim",
  "whiteoak",
  "zerodha",
  "groww mutual fund"
];

export const KNOWLEDGE_CHUNKS = [
  // HDFC Mid-Cap Opportunities
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_fund_overview",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "fund_overview",
    content: "HDFC Mid-Cap Opportunities Fund (Direct Plan - Growth Option) is managed by HDFC Asset Management Company Limited under the Equity: Mid Cap category. It is an Open-ended equity scheme predominantly investing in mid cap stocks tracking the NIFTY Midcap 150 TRI benchmark with Very High risk.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["overview", "category", "benchmark", "riskometer", "classification", "amc"]
  },
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_expense_ratio",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "expense_ratio",
    content: "The Total Expense Ratio (TER) for HDFC Mid-Cap Opportunities Fund Direct Plan - Growth is 0.74% (inclusive of GST).",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["expense ratio", "ter", "management fee", "charges", "fees", "cost"]
  },
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_exit_load",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "exit_load",
    content: "An exit load of 1.00% is applicable for units redeemed or switched out within 1 year (365 days) from the date of allotment. No exit load is payable for units redeemed after 1 year.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["exit load", "redemption fee", "holding period", "early withdrawal", "exit charges", "redeem"]
  },
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_investment_limits",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "investment_limits",
    content: "The minimum SIP investment amount is ₹100 per installment. The minimum lump sum investment amount for initial as well as additional purchases is ₹100.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["minimum sip", "min sip", "lump sum", "minimum investment", "initial purchase", "sip amount"]
  },
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_lock_in_period",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "lock_in_period",
    content: "Nil. This is an open-ended equity fund with no statutory lock-in period.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["lock in", "lock-in", "lock-in period", "holding lock", "maturity", "lockin"]
  },
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_taxation",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "taxation",
    content: "STCG is taxed at 20% if redeemed within 12 months. LTCG above ₹1.25 Lakh in a financial year is taxed at 12.5% without indexation if held for more than 12 months.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["taxation", "stcg", "ltcg", "capital gains", "80c", "tax benefit", "tax"]
  },
  {
    chunk_id: "hdfc_mid_cap_fund_direct_growth_operations",
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    parameter: "operations",
    content: "Account statements and capital gains reports can be downloaded online from the Groww App under Profile > Reports or directly via the HDFC MF online investor portal using your PAN and Folio number.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    keywords: ["download statement", "statement", "folio", "cams", "account statement", "report"]
  },

  // HDFC Small Cap Fund
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_fund_overview",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "fund_overview",
    content: "HDFC Small Cap Fund (Direct Plan - Growth Option) is managed by HDFC Asset Management Company Limited under the Equity: Small Cap category. It tracks the BSE 250 SmallCap TRI benchmark and is classified as 'Very High' risk on the SEBI Riskometer.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["overview", "category", "benchmark", "riskometer", "classification"]
  },
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_expense_ratio",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "expense_ratio",
    content: "The Total Expense Ratio (TER) for HDFC Small Cap Fund Direct Plan - Growth is 0.68% (inclusive of GST).",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["expense ratio", "ter", "management fee", "charges", "fees", "cost"]
  },
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_exit_load",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "exit_load",
    content: "An exit load of 1.00% is charged if units are redeemed or switched out within 1 year (365 days) from allotment. Nil exit load after 1 year.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["exit load", "redemption fee", "holding period", "early withdrawal", "exit charges", "redeem"]
  },
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_investment_limits",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "investment_limits",
    content: "The minimum SIP investment is ₹100 per installment. The minimum lump sum purchase amount is ₹100 for both initial and additional purchases.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["minimum sip", "min sip", "lump sum", "minimum investment", "initial purchase", "sip amount"]
  },
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_lock_in_period",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "lock_in_period",
    content: "Nil. This is an open-ended equity fund with no statutory lock-in period.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["lock in", "lock-in", "lock-in period", "holding lock", "maturity", "lockin"]
  },
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_taxation",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "taxation",
    content: "STCG is taxed at 20% if redeemed within 12 months. LTCG above ₹1.25 Lakh per financial year is taxed at 12.5% without indexation if held for more than 12 months.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["taxation", "stcg", "ltcg", "capital gains", "80c", "tax benefit", "tax"]
  },
  {
    chunk_id: "hdfc_small_cap_fund_direct_growth_operations",
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    parameter: "operations",
    content: "Investors can generate consolidated or scheme-specific account statements from the Groww App (Profile > Reports > Mutual Fund Statements) or via the HDFC MF portal.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    keywords: ["download statement", "statement", "folio", "cams", "account statement", "report"]
  },

  // HDFC Top 100 / Large Cap
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_fund_overview",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "fund_overview",
    content: "HDFC Top 100 / Large Cap Fund (Direct Plan - Growth Option) is managed by HDFC Asset Management Company Limited under the Equity: Large Cap category tracking the NIFTY 100 TRI benchmark with Very High risk.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["overview", "category", "benchmark", "riskometer", "classification"]
  },
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_expense_ratio",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "expense_ratio",
    content: "The Total Expense Ratio (TER) for HDFC Top 100 Fund Direct Plan - Growth is 1.08%.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["expense ratio", "ter", "management fee", "charges", "fees", "cost"]
  },
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_exit_load",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "exit_load",
    content: "An exit load of 1.00% is levied if units are redeemed or switched out within 1 year (365 days) from allotment. Nil exit load after 1 year.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["exit load", "redemption fee", "holding period", "early withdrawal", "exit charges", "redeem"]
  },
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_investment_limits",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "investment_limits",
    content: "The minimum SIP investment is ₹100 per installment. The minimum initial and additional lump sum investment is ₹100.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["minimum sip", "min sip", "lump sum", "minimum investment", "initial purchase", "sip amount"]
  },
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_lock_in_period",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "lock_in_period",
    content: "Nil. This open-ended equity fund carries no statutory lock-in period.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["lock in", "lock-in", "lock-in period", "holding lock", "maturity", "lockin"]
  },
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_taxation",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "taxation",
    content: "STCG is taxed at 20% if redeemed within 12 months. LTCG above ₹1.25 Lakh per financial year is taxed at 12.5% without indexation if held for more than 12 months.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["taxation", "stcg", "ltcg", "capital gains", "80c", "tax benefit", "tax"]
  },
  {
    chunk_id: "hdfc_large_cap_fund_direct_growth_operations",
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    parameter: "operations",
    content: "Obtain account and tax statements online through Groww (Reports section) or by visiting the HDFC Mutual Fund investor service portal.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    keywords: ["download statement", "statement", "folio", "cams", "account statement", "report"]
  },

  // HDFC ELSS Tax Saver
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_fund_overview",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "fund_overview",
    content: "HDFC ELSS Tax Saver Fund (Direct Plan - Growth Option) is an open-ended equity linked saving scheme with a statutory lock-in of 3 years and tax deduction benefit under Section 80C, tracking the NIFTY 500 TRI benchmark with Very High risk.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["overview", "category", "benchmark", "riskometer", "classification", "80c"]
  },
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_expense_ratio",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "expense_ratio",
    content: "The Total Expense Ratio (TER) for HDFC ELSS Tax Saver Fund Direct Plan - Growth is 1.09%.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["expense ratio", "ter", "management fee", "charges", "fees", "cost"]
  },
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_exit_load",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "exit_load",
    content: "Nil. No exit load is charged for redemption after the completion of the statutory 3-year lock-in period.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["exit load", "redemption fee", "holding period", "early withdrawal", "exit charges", "redeem"]
  },
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_investment_limits",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "investment_limits",
    content: "The minimum SIP investment is ₹500 and in multiples of ₹500. The minimum lump sum investment amount is ₹500 for initial as well as additional purchases.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["minimum sip", "min sip", "lump sum", "minimum investment", "initial purchase", "sip amount"]
  },
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_lock_in_period",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "lock_in_period",
    content: "Mandatory 3-year (36 months) lock-in period from the date of allotment for each installment. Units cannot be redeemed, transferred, or switched out during the lock-in period.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["lock in", "lock-in", "lock-in period", "holding lock", "maturity", "3 years", "lockin"]
  },
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_taxation",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "taxation",
    content: "Investments qualify for tax deduction under Section 80C of the Income Tax Act up to ₹1.5 Lakh per financial year. LTCG above ₹1.25 Lakh upon redemption after 3 years is taxed at 12.5% without indexation.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["taxation", "stcg", "ltcg", "capital gains", "80c", "tax benefit", "tax deduction", "tax saving"]
  },
  {
    chunk_id: "hdfc_elss_tax_saver_fund_direct_plan_growth_operations",
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    parameter: "operations",
    content: "Tax saving investment certificates (80C proofs) and account statements can be downloaded via Groww Profile > Reports > Capital Gains & Tax Reports or via HDFC MF website.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    keywords: ["download statement", "statement", "folio", "cams", "account statement", "report", "80c certificate"]
  },

  // HDFC Gold ETF FoF
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_fund_overview",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "fund_overview",
    content: "HDFC Gold ETF Fund of Fund (Direct Plan - Growth Option) is an Open-ended Fund of Fund scheme investing in units of HDFC Gold Exchange Traded Fund (ETF) tracking Domestic Physical Gold with High risk.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["overview", "category", "benchmark", "riskometer", "classification"]
  },
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_expense_ratio",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "expense_ratio",
    content: "The Total Expense Ratio (TER) for HDFC Gold ETF Fund of Fund Direct Plan - Growth is 0.25% (investors also bear underlying ETF scheme expenses).",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["expense ratio", "ter", "management fee", "charges", "fees", "cost"]
  },
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_exit_load",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "exit_load",
    content: "An exit load of 1.00% is applicable if units are redeemed or switched out on or before 15 days from the date of allotment. No exit load is payable if redeemed after 15 days.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["exit load", "redemption fee", "holding period", "early withdrawal", "exit charges", "redeem"]
  },
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_investment_limits",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "investment_limits",
    content: "The minimum SIP investment is ₹100 per installment. The minimum lump sum investment amount is ₹100 for initial as well as additional purchases.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["minimum sip", "min sip", "lump sum", "minimum investment", "initial purchase", "sip amount"]
  },
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_lock_in_period",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "lock_in_period",
    content: "Nil. There is no statutory lock-in period for this fund of funds scheme.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["lock in", "lock-in", "lock-in period", "holding lock", "maturity", "lockin"]
  },
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_taxation",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "taxation",
    content: "Specified Mutual Fund / Debt & Commodities Taxation rules apply as per Finance Act provisions based on holding duration and investor tax slab.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["taxation", "stcg", "ltcg", "capital gains", "80c", "tax benefit", "tax"]
  },
  {
    chunk_id: "hdfc_gold_etf_fund_of_fund_direct_plan_growth_operations",
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    parameter: "operations",
    content: "Download statements via Groww Profile > Reports > Mutual Funds or through HDFC AMC / CAMS online facilities using PAN and folio number.",
    official_source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    keywords: ["download statement", "statement", "folio", "cams", "account statement", "report"]
  },

  // General Operations Chunks
  {
    chunk_id: "general_operations_statement_download",
    scheme_code: "general-operations",
    parameter: "statement_download_general",
    content: "To download statements on Groww: Open Groww App > Profile > Reports > Mutual Fund Statements or Capital Gains Report. Statements can also be obtained directly from HDFC AMC Investor Services or via CAMS/KFintech CAS portals.",
    official_source_url: "https://groww.in/mutual-funds",
    keywords: ["download statement", "statement", "account statement", "groww statement", "cas statement", "cams", "kfintech"]
  },
  {
    chunk_id: "general_operations_capital_gains_report",
    scheme_code: "general-operations",
    parameter: "capital_gains_report_general",
    content: "Capital gains tax reports for ITR filing (Schedule 112A) are accessible on Groww under Profile > Reports > Capital Gains Report by selecting the required Assessment Year.",
    official_source_url: "https://groww.in/mutual-funds",
    keywords: ["capital gains report", "tax statement", "schedule 112a", "itr filing", "tax report download"]
  },
  {
    chunk_id: "general_operations_educational_resources",
    scheme_code: "general-operations",
    parameter: "educational_resources_general",
    content: "For investor education and mutual fund guidelines, consult Groww Mutual Funds (https://groww.in/mutual-funds), AMFI Knowledge Center (https://www.amfiindia.com), or the SEBI Investor Portal (https://investor.sebi.gov.in).",
    official_source_url: "https://groww.in/mutual-funds",
    keywords: ["amfi", "sebi", "investor education", "guidelines", "regulations"]
  }
];
