export const fmtMoney = (v) => new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 2,
}).format(Number(v))

export const fmtMoneyShort = (v) => new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 0,
}).format(Number(v))

export const fmtNumber = (v) => new Intl.NumberFormat('en-US').format(Number(v))

export const fmtDate = (v) => {
  if (!v) return '—'
  return new Date(v).toLocaleDateString('ru-RU', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

export const fmtDateTime = (v) => {
  if (!v) return '—'
  return new Date(v).toLocaleString('ru-RU', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export const STATUS_MAP = {
  draft:      { label: 'Черновик',   severity: 'secondary', icon: 'pi pi-pencil' },
  assigned:   { label: 'Назначен',   severity: 'warn',      icon: 'pi pi-user' },
  in_transit: { label: 'В пути',     severity: 'info',      icon: 'pi pi-truck' },
  delivered:  { label: 'Доставлено', severity: 'success',   icon: 'pi pi-check' },
  cancelled:  { label: 'Отменен',    severity: 'danger',    icon: 'pi pi-times' },
}