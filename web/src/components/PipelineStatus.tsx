import { formatNumber } from "@/lib/format";
import type { DashboardData } from "@/lib/types";

const DEPLOY_ENV = process.env.NEXT_PUBLIC_DEPLOY_ENV ?? "local";

/** Shows where the numbers came from: every figure is traceable to a pipeline run. */
export function PipelineStatus({ data }: { data: DashboardData }) {
  const { quality, build, generatedAt } = data;
  const stages = ["Lint & test", "Data quality", "Build", "Deploy"];

  return (
    <section className="card pipeline" aria-label="Pipeline status">
      <div className="pipeline-head">
        <div>
          <div className="pipeline-title">Delivered by CI/CD</div>
          <div className="pipeline-sub">
            {formatNumber(quality.rows)} rows from {quality.files} daily files passed every
            data-quality check before publishing.
          </div>
        </div>
        <span className={`env env-${DEPLOY_ENV}`}>{DEPLOY_ENV}</span>
      </div>

      <ol className="stages">
        {stages.map((s) => (
          <li key={s}>
            <span className="tick" aria-hidden>
              ✓
            </span>
            {s}
          </li>
        ))}
      </ol>

      <dl className="meta">
        <div>
          <dt>Commit</dt>
          <dd>
            <code>{build.commit}</code>
          </dd>
        </div>
        <div>
          <dt>Pipeline run</dt>
          <dd>
            {build.runUrl ? (
              <a href={build.runUrl} target="_blank" rel="noreferrer">
                #{build.runNumber}
              </a>
            ) : (
              "local build"
            )}
          </dd>
        </div>
        <div>
          <dt>Data generated</dt>
          <dd>{generatedAt.replace("T", " ").replace("+00:00", " UTC")}</dd>
        </div>
      </dl>
    </section>
  );
}
