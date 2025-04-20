import { parse } from 'date-fns'


/**
 * Helper function used to parse dates in the format dd-MM-yyyy. Also saves the original date in a new field.
 * @param {Array} data - The data to parse the dates from. An array of objects.
 * @param {String} dateField - The field that contains the date to parse. String with the name of the field.
 * @returns {Array} - The data with the parsed dates.
 */
export const parseDates = (data, dateField) => {
  return data.map((record) => ({
    ...record,
    [`original_${dateField}`]: record[dateField],
    [dateField]: parse(record[dateField], 'dd-MM-yyyy', new Date()),
  }))
}
