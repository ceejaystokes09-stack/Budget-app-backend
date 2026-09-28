import '../index.css'
function Footer({ onAddTask, canAddTask }){
    const ChangeTab = (e)=>{
        console.log("vn")
        document.querySelectorAll(".bottom-nav .bottom-nav__item").forEach(el=>{
            el.classList.remove("is-active")
        })
        e.currentTarget.classList.add("is-active")
    }   

    return (
        <footer className="bottom-nav">
            <div className="bottom-nav__item is-active" onClick={ChangeTab}>
                <i className="fa-solid fa-house" aria-hidden="true"></i>
                <p className='cut'>Home</p>
            </div>
            <div className={`bottom-nav__item ${canAddTask ? "" : "is-disabled"}`} onClick={canAddTask ? onAddTask : undefined} aria-disabled={!canAddTask}>
                <i className="fa-solid fa-plus" aria-hidden="true"></i>
                <p className='cut'>Add</p>
            </div>
            <div className="bottom-nav__item" onClick={ChangeTab}>
                <i className="fa-solid fa-user" aria-hidden="true"></i>
                <p className='cut'>Account</p>
            </div>
        </footer>
    )
}

export default Footer