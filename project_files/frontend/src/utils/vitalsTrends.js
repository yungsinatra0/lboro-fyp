/**
 * Helper function to calculate the trend of a lab result based on its value and reference range. Will select the latest value for each type of health data and determine if it is stable, up, or down based on the given reference range.
 * @param {Array} healthdata - Array of health data objects
 * @returns {Array} - Array of health data objects with trend information. Contains one of each type of health data with the latest value and its trend (stable, up, down).
 */
export const groupCompareHealthdata = (healthdata) => {
  const groupedData = {}

  // Group the health data by type name
  for (const data of healthdata) {
    if (!groupedData[data.name]) {
      groupedData[data.name] = []
    }
    groupedData[data.name].push(data)
  }

  const dataTrends = []

  // Process each group
  // eslint-disable-next-line no-unused-vars
  for (const [key, values] of Object.entries(groupedData)) {
    if (!values || values.length === 0) {
      continue
    }

    const latest = values[0]
    let trend = 'stable'

    if (latest.name === 'Înălțime' || latest.name === 'Greutate') {
      trend = 'stable'
    } else if (latest.name === 'Tensiune arterială') {
      const rangeStr = latest.normal_range

      if (rangeStr) {
        const [low, high] = rangeStr.split(' - ')
        const lowSys = parseFloat(low.split('/')[0].trim())
        const highSys = parseFloat(high.split(' ')[0].split('/')[0].trim())

        if (latest.value_systolic > highSys) {
          trend = 'up'
        } else if (latest.value_systolic < lowSys) {
          trend = 'down'
        }
      }
    } else if (latest.normal_range) {
      const rangeStr = latest.normal_range

      try {
        const [low, high] = rangeStr.split(' - ')
        const rangeMin = parseFloat(low.trim())
        const rangeMax = parseFloat(high.split(' ')[0].trim())

        if (latest.value > rangeMax) {
          trend = 'up'
        } else if (latest.value < rangeMin) {
          trend = 'down'
        }
      } catch (error) {
        console.error('Error parsing normal range:', error)
        trend = 'stable'
      }
    }

    dataTrends.push({
      ...latest,
      trend: trend,
    })
  }

  return dataTrends
}
