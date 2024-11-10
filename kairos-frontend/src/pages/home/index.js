

export default function Home() {
	return (
		<div className="card w-[48em] flex flex-col items-center gap-2 py-8">
			<h1 className="w-full text-3xl text-center">this is the home</h1>
				
            <li>
			    <a href="/assignments">Assignments</a>
			</li>
            <li>
				<a href="/calendar">Calender</a>
			</li>
            <li>
				<a href="/settings">Settings</a>
			</li>

		</div>
	)
}