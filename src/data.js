import { csvParse } from "d3";
import optText from "../data/processed/opt_growth.csv?raw";
import employerText from "../data/processed/h1b_employers.csv?raw";
import industryText from "../data/processed/h1b_industries.csv?raw";
import distributionText from "../data/processed/uscis_fy2025_distribution.csv?raw";
import primaryIndustryText from "../data/processed/uscis_fy2025_industries.csv?raw";
import overlapText from "../data/processed/opt_h1b_employer_overlap.csv?raw";
import optEmployerText from "../data/processed/opt_employers.csv?raw";
import matchAuditText from "../data/processed/opt_h1b_match_audit.csv?raw";
import { parseIndustries, parseOverlap, parseOptEmployers } from "./chartData";
import validation from "../data/processed/validation.json";
import manifest from "../data/raw/manifest.json";
import { parseEmployerDistribution } from "./distribution";

export const opt = csvParse(optText, (d) => ({
  ...d,
  start_year: +d.start_year,
  opt_students: +d.opt_students,
  enrolled_students: +d.enrolled_students,
  total_international_students: +d.total_international_students,
}));
export const employers = csvParse(employerText, (d) => ({
  ...d,
  initial_approvals: +d.initial_approvals,
}));
export const industries = csvParse(industryText, (d) => ({
  ...d,
  initial_approvals: +d.initial_approvals,
}));
export const employerDistribution = parseEmployerDistribution(distributionText);
export const primaryIndustries = parseIndustries(primaryIndustryText);
export const overlap = parseOverlap(overlapText);
export const optEmployers = parseOptEmployers(optEmployerText);
export const matchAudit = csvParse(matchAuditText);
export const distribution = {
  employers_with_initial_approval: employerDistribution.total.population_employers,
  employer_share_exactly_1_initial_approval: employerDistribution.bins[0].employer_share_percent.toFixed(1),
  employer_share_1_to_10_initial_approvals: employerDistribution.bins.slice(0, 3).reduce((sum, d) => sum + d.employer_share_percent, 0).toFixed(1),
};
export const latest = opt.at(-1);
export const previous = opt.at(-2);
export const growth = (latest.opt_students / previous.opt_students - 1) * 100;
export const nfapUrl = employers[0].source_url;
export const optUrl = latest.source_url;
export { validation, manifest };

// Vite bundles the same CSVs the pipeline writes. No hand-maintained public copy.
const urls = import.meta.glob("../data/processed/*.csv", {
  query: "?url",
  import: "default",
  eager: true,
});
export const downloads = Object.entries(urls).map(([path, url]) => ({
  name: path.split("/").at(-1),
  url,
}));
export const number = (value) => new Intl.NumberFormat("en-US").format(value);
