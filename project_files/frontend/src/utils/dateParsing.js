import { parse } from 'date-fns'

export const parseDates = (data, dateField) => {
  return data.map((record) => ({
    ...record,
    [`original_${dateField}`]: record[dateField],
    [dateField]: parse(record[dateField], 'dd-MM-yyyy', new Date()),
  }))
}
