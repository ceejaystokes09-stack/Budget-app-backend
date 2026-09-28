import "../index.css"

function Progress({ Current, Max, Colors }) {
    const safeMax = Number(Max) || 1
    const percent = Math.min((Number(Current) / safeMax) * 100, 100)
    const fill = Colors?.[0] || "#4cc9f0"
    const track = Colors?.[1] || "#e2e8f0"

    return (
        <div className="task-progress-wrap">
            <div className="task-progress-meta">
                <span>Progress</span>
                <strong>{Math.round(percent)}%</strong>
            </div>
            <div className="task-progress-bar" aria-label={`Progress ${Math.round(percent)} percent`}>
                <div
                    className="task-progress-fill"
                    style={{
                        width: `${percent}%`,
                        background: `linear-gradient(90deg, ${fill} 0%, ${fill} 72%, #6ee7b7 100%)`,
                    }}
                />
            </div>
            <div className="task-progress-amount">
                <span>{Current}</span>
                <span>{Max}</span>
            </div>
        </div>
    )
}

export default Progress