import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const RADIAN = Math.PI / 180
const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.05) return null
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  return (
    <text x={x} y={y} fill="rgba(255,255,255,0.8)" textAnchor="middle" dominantBaseline="central" fontSize={11}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-strong border border-cyber-border rounded-lg p-3 text-sm">
        <p style={{ color: payload[0].payload.color }} className="font-medium capitalize">
          {payload[0].name}: {payload[0].value}
        </p>
      </div>
    )
  }
  return null
}

const SEVERITY_COLORS = {
  critical: '#ff3366',
  high: '#ff6b35',
  medium: '#f59e0b',
  low: '#10b981',
  info: '#3b82f6',
}

export function SeverityDonut({ data, height = 200 }) {
  const chartData = Object.entries(data || {}).map(([name, value]) => ({
    name,
    value,
    color: SEVERITY_COLORS[name] || '#00d4ff',
  }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={80}
          paddingAngle={3}
          dataKey="value"
          labelLine={false}
          label={renderCustomLabel}
        >
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.color} stroke="rgba(0,0,0,0.3)" strokeWidth={1} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 11, textTransform: 'capitalize' }}>{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
