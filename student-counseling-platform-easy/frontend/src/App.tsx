import {BrowserRouter,Route,Routes} from 'react-router-dom'
import {AuthProvider} from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './layouts/AppLayout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UserListPage from './pages/UserListPage'
import StudentsPage from './pages/StudentsPage'
import StudentDetailPage from './pages/StudentDetailPage'
import RecordOverviewPage from './pages/RecordOverviewPage'
import ProgramReviewsPage from './pages/ProgramReviewsPage'
import ReportsPage from './pages/ReportsPage'
function NotFound(){return <div className="card p-8 text-center"><h1 className="text-xl font-bold">صفحه پیدا نشد</h1><a className="btn-primary mt-4" href="/">بازگشت به داشبورد</a></div>}
export default function App(){return <BrowserRouter><AuthProvider><Routes><Route path="/login" element={<LoginPage/>}/><Route element={<ProtectedRoute/>}><Route element={<AppLayout/>}><Route index element={<DashboardPage/>}/><Route element={<ProtectedRoute roles={['ADMIN']}/>}><Route path="users" element={<UserListPage title="کاربران"/>}/><Route path="supervisors" element={<UserListPage fixedRole="SUPERVISOR" title="ناظران"/>}/></Route><Route element={<ProtectedRoute roles={['ADMIN','SUPERVISOR']}/>}><Route path="advisors" element={<UserListPage fixedRole="ADVISOR" title="مشاوران"/>}/><Route path="reports" element={<ReportsPage/>}/></Route><Route path="students" element={<StudentsPage/>}/><Route path="students/:id" element={<StudentDetailPage/>}/><Route path="weekly" element={<RecordOverviewPage kind="weekly"/>}/><Route path="assessments" element={<RecordOverviewPage kind="assessments"/>}/><Route path="challenges" element={<RecordOverviewPage kind="challenges"/>}/><Route path="program-reviews" element={<ProgramReviewsPage/>}/><Route path="*" element={<NotFound/>}/></Route></Route></Routes></AuthProvider></BrowserRouter>}
