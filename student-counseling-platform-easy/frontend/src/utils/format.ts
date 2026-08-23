export const faDate=(value?:string|null)=>{if(!value)return '—';const normalized=/^\d{4}-\d{2}-\d{2}$/.test(value)?`${value}T00:00:00`:value;return new Intl.DateTimeFormat('fa-IR-u-ca-persian',{year:'numeric',month:'short',day:'numeric'}).format(new Date(normalized))}
export const faNumber=(value:number|string|null|undefined)=>value===null||value===undefined?'—':new Intl.NumberFormat('fa-IR').format(Number(value))
export const roleLabel=(role:string)=>({ADMIN:'مدیر',SUPERVISOR:'ناظر',ADVISOR:'مشاور'}[role]||role)
export const errorMessage=(e:any)=>{
  const data=e?.response?.data
  if(typeof data?.detail==='string') return data.detail
  if(data && typeof data==='object'){const first=Object.values(data)[0] as any; if(Array.isArray(first)) return String(first[0]); if(typeof first==='string') return first; if(first && typeof first==='object') return JSON.stringify(first)}
  if(e?.message==='Network Error') return 'ارتباط با سرور برقرار نشد.'
  return 'خطایی رخ داد. لطفاً دوباره تلاش کنید.'
}
