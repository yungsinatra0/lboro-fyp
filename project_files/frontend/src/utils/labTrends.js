/**
 * Helper function to calculate the trend of a lab result based on its value and reference range.
 * @param {Number} value - The lab result value.
 * @param {String} reference_range - The reference range for the lab result, which can be a string with various formats (e.g., "10-20", ">10", "<20", "normal", etc.).
 * @param {Boolean} is_numeric - Indicates whether the lab result is numeric or not.
 * @returns {string} 'up', 'down', or 'normal' based on the trend of the lab result.
 */
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
    // At the moment, returns 'normal' for any non-numeric value
    return null
  }
  return 'normal'
}


/**
 * Helper function to generate chart data for lab results. Will create the data for point colors, but also the data and labels for the chart itself.
 * @param {Array} results - The lab results data for one specific test (e.g. Hemoglobin), which should be an array of objects of type LabResultResponse containing the lab result information.
 * @returns {Object} An object containing the labels and datasets for the chart.
 */
export const getChartData = (results) => {
  // Filter out non-numeric results and reverse the order to have the most recent date first. Also keeps the original object structure that is used later in the function.
  const numericResults = results.filter((result) => result.is_numeric === true).reverse()
  // Array of number containing only the parsed values of the lab results
  const data = numericResults.map((result) => parseFloat(result.value))
  // Labels are the dates of the lab results, and data is the values of the lab results
  const labels = numericResults.map((result) => result.original_date_collection)

  // Compute the point colors based on the trend of each lab result
  const pointBackgroundColors = numericResults.map((result) => {
    const trend = calculateTrend(result.value, result.reference_range, result.is_numeric)
    if (trend === 'up' || trend === 'down') return '#dc3545'
    return '#36c02c'
  })

  // Same as above, but for the border color of the points
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
