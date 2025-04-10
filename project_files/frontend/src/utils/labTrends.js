export const calculateTrend = (value, reference_range, is_numeric) => {
    if (!value || !reference_range) return null
  
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