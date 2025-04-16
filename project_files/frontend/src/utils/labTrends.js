export const calculateTrend = (value, reference_range, is_numeric) => {
    if (!value || !reference_range) return 'normal'
  
    if (is_numeric) {
      value = parseFloat(value)
      if (reference_range.includes('-')) {
        const [min, max] = reference_range.split('-').map(Number)
        if (value < min) return 'down'
        if (value > max) return 'up'
      } else if (reference_range.includes('>')) {
        const min = parseFloat(reference_range.replace('>', ''))
        if (value < min) return 'down'
        return 'normal'
      } else if (reference_range.includes('<')) {
        const max = parseFloat(reference_range.replace('<', ''))
        if (value > max) return 'up'
        return 'normal'
      } else {
        let reference = parseFloat(reference_range)
        if (value < reference) return 'down'
        if (value > reference) return 'up'
        return 'normal'
      }
    } else if (is_numeric === false) {
      // Handle non-numeric values (e.g., positive/negative, normal/abnormal)
      return null
    }
    return 'normal'
  }

export const getChartData = (results) => {
  const numericResults = results.filter((result) => result.is_numeric === true).reverse()
  const labels = numericResults.map((result) => result.original_date_collection)
  const data = numericResults.map((result) => parseFloat(result.value))

  const pointBackgroundColors = numericResults.map((result) => {
    const trend = calculateTrend(result.value, result.reference_range, result.is_numeric)
    if (trend === 'up' || trend === 'down') return '#dc3545'
    return '#36c02c'
  })

  const pointBorderColors = numericResults.map((result) => {
    const trend = calculateTrend(result.value, result.reference_range, result.is_numeric)
    if (trend === 'up' || trend === 'down') return '#dc3545'
    return '#36c02c'
  })

  return {
    labels,
    datasets: [
      {
        data,
        borderColor: '#9e9e9e',
        tension: 0.4,
        borderWidth: 1,
        pointRadius: 3,
        pointBackgroundColor: pointBackgroundColors,
        pointBorderColor: pointBorderColors,
      },
    ],
  }
}