import "../index.css"
import { useState } from "react"
import Task from "./Task"

function Group({ group, groups, tasks, onAddTask, onUpdateTask }) {
    const [isOpen, setIsOpen] = useState(true)
    const children = groups.filter((item) => item.parentId === group.id)
    const groupTasks = tasks.filter((task) => task.groupId === group.id)

    return (
        <article className="group-card">
            <div className="group-header">
                <button
                    type="button"
                    className="group-toggle"
                    aria-expanded={isOpen}
                    onClick={() => setIsOpen(!isOpen)}
                >
                    <span className={`group-chevron ${isOpen ? "is-open" : ""}`} aria-hidden="true">›</span>
                    <span className="group-heading-text">
                        <span className="group-title">{group.name}</span>
                        <span className="group-location">
                            {group.parentId
                                ? `Inside ${groups.find((item) => item.id === group.parentId)?.name || "another group"}`
                                : "Top-level group"}
                        </span>
                    </span>
                </button>
                <button type="button" className="group-add-task" onClick={() => onAddTask(group.id)}>
                    <span aria-hidden="true">+</span> Add task
                </button>
            </div>

            {isOpen && (
                <div className="group-content">
                    {groupTasks.length > 0 ? (
                        <div className="group-task-list">
                            {groupTasks.map((task) => (
                                <Task
                                    key={task.id}
                                    Id={task.id}
                                    Name={task.name}
                                    Desc={task.description}
                                    Max={task.maxPrice}
                                    Current={task.currentPrice}
                                    Status={task.isComplete}
                                    onUpdate={onUpdateTask}
                                />
                            ))}
                        </div>
                    ) : (
                        <p className="group-empty-tasks">No tasks in this group yet.</p>
                    )}
                    {children.length > 0 && (
                        <div className="nested-groups">
                            <p className="nested-groups-label">SUBGROUPS <span>{children.length}</span></p>
                            {children.map((child) => (
                                <Group key={child.id} group={child} groups={groups} tasks={tasks} onAddTask={onAddTask} onUpdateTask={onUpdateTask} />
                            ))}
                        </div>
                    )}
                </div>
            )}
        </article>
    )
}

export default Group
