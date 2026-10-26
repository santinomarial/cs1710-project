import { useState } from "react";
import { employers, number } from "../data";

export default function EmployerTable() {
  const [query, setQuery] = useState("");
  const [all, setAll] = useState(false);
  const matches = employers.filter((d) =>
    d.employer_name.toLowerCase().includes(query.toLowerCase()),
  );
  const visible = all || query ? matches : matches.slice(0, 10);
  return (
    <details className="employer-detail">
      <summary>
        Explore the 100 listed employers <span>+</span>
      </summary>
      <p>
        This table covers employers with 100+ initial approvals in NFAP’s
        appendix. It cannot show the full national distribution.
      </p>
      <label className="search-label" htmlFor="employer-search">
        Find a listed employer
      </label>
      <input
        id="employer-search"
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Try Harvard, Mayo, or Microsoft"
      />
      <p className="small" role="status">
        Showing {visible.length} of {matches.length} matching records.
      </p>
      <div className="table-scroll">
        <table>
          <caption>
            FY2025 · initial employment approvals · NFAP Appendix Table 2
          </caption>
          <thead>
            <tr>
              <th scope="col">Employer, as reported</th>
              <th scope="col">Approvals</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((d) => (
              <tr key={d.employer_key}>
                <th scope="row">{d.employer_name}</th>
                <td>{number(d.initial_approvals)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!matches.length && (
        <p>
          No matching employer in this partial list. This does not mean the
          employer had no approvals.
        </p>
      )}
      {!query && (
        <button onClick={() => setAll(!all)}>
          {all ? "Show first 10" : "Show all 100"} {all ? "−" : "+"}
        </button>
      )}
    </details>
  );
}
