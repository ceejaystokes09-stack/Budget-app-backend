import "../index.css"
import { useEffect, useState } from "react"

function Edit({ task, onClose }) {
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        const frame = requestAnimationFrame(() => setIsVisible(true))
        return () => cancelAnimationFrame(frame)
    }, [])

    if (!task) return null

    function handleClose() {
        setIsVisible(false)
        window.setTimeout(onClose, 200)
    }

    function Save(){
        const updatedTask = {
            ...task,
            name: document.querySelector(".Task-edit #new-name").value.trim(),
            description: document.querySelector(".Task-edit #new-desc").value.trim(),
            maxPrice: Number(document.querySelector(".Task-edit #new-max").value) || 0,
            currentPrice: Number(document.querySelector(".Task-edit #new-Current").value) || 0,
        }

        const savedTasks = JSON.parse(localStorage.getItem("tasks") || "[]")
        const updatedTasks = savedTasks.map((savedTask) => (
            savedTask.id === task.id ? updatedTask : savedTask
        ))

        localStorage.setItem("tasks", JSON.stringify(updatedTasks))
        window.dispatchEvent(new Event("tasksUpdated"))
        handleClose()
    }

    return (
        <div className={`Task-edit ${isVisible ? "is-visible" : ""}`}>
            <div className="Task-edit__panel">
                <div className="Task-edit__header">
                    <h3>Edit Task</h3>
                    <button type="button" className="Task-edit__save" onClick={Save} >Save</button>
                    <button type="button" className="Task-edit__close" onClick={handleClose}>✕</button>
                    
                </div>

                <label>
                    Name
                    <input defaultValue={task.name} id="new-name" />
                </label>

                <label>
                    Description
                    <textarea defaultValue={task.description} rows="4" id="new-desc" />
                </label>

                <div className="Task-edit__row">
                    <label>
                        Max
                        <input type="number" defaultValue={task.maxPrice} id="new-max" />
                    </label>

                    <label>
                        Current
                        <input type="number" defaultValue={task.currentPrice} id="new-Current" />
                    </label>
                </div>

                <button type="button" className="Task-edit__complete">Mark As Complete</button>
            </div>
        </div>
    )
}

export default Edit