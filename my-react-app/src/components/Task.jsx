import "../index.css"
import { useState } from "react"
import Progress from "./Progress"
import Edit from "./Task-edit"

function Task({ Id, Name, Desc, Current, Max, Status }) {
    const [isEditing, setIsEditing] = useState(false)
    const accentColor = Status ? "#5eead4" : "#7c3aed"

    return (
        <>
            <div className="Task start" onClick={() => setIsEditing(true)}>
                <div className="Task-Warning" style={{ background: accentColor }}></div>
                <div className="Full-width Task-info">
                    <div className="task-header-row">
                        <h2>{Name}</h2>
                        <span className={`task-type-badge ${Status ? "Completed" : "In-Progress"}`}>
                            {Status ? "Completed" : "In Progress"}
                        </span>
                    </div>
                    <p>{Desc}</p>
                    <Progress Current={Current} Max={Max} Colors={[accentColor, "#e5e7eb"]} />
                </div>
            </div>

            {isEditing && (
                <Edit
                    task={{ id: Id, name: Name, description: Desc, maxPrice: Max, currentPrice: Current, isGroup: Status }}
                    onClose={() => setIsEditing(false)}
                />
            )}
        </>
    )
}

export default Task