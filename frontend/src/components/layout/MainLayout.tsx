import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function MainLayout() {
  return (
    <div className="flex h-screen bg-cyber-black text-gray-100 overflow-hidden relative">
      {/* Dynamic Background Overlay */}
      <div className="fixed inset-0 cyber-bg pointer-events-none"></div>
      
      {/* Ambient Light Effects */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-cyber-blue/5 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="fixed bottom-0 left-0 w-[400px] h-[400px] bg-cyber-purple/5 blur-[100px] rounded-full pointer-events-none"></div>

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col relative z-10 overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-10 custom-scrollbar">
          <div className="max-w-[1600px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
