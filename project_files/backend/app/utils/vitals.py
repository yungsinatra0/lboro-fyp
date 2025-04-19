from ..models import HealthData

def group_compare_healthdata(healthdata: list[HealthData]):
    """
    Process health data records and determine trends based on normal ranges.
    
    This function groups health data by type, analyzes the most recent value 
    for each type, and determines whether it falls within the normal range.
    It then assigns a trend indicator ('up', 'down', or 'stable') based on 
    the comparison with normal ranges.
    
    The function handles both simple health data types (like height, weight)
    and complex ones (like blood pressure) which require special processing.
    
    Args:
        healthdata: List of HealthData objects to process
        
    Returns:
        list: A list of dictionaries containing the latest health data item
              for each type and its associated trend indicator
    """
    grouped_data = {}
    
    for data in healthdata:
        if data.type.name not in grouped_data:
            grouped_data[data.type.name] = []
        grouped_data[data.type.name].append(data)
        
    data_trends = []        
    for key, values in grouped_data.items():
        if not values:
            continue
        
        latest = values[0]
        trend = "stable"
        
        if latest.type.name in ["Înălțime", "Greutate"]:
            trend = "stable"

        elif latest.type.name == "Tensiune arterială":
            range_str = latest.type.normal_range
            if range_str:
                low, high = range_str.split(" - ")
                low_sys = float(low.split("/")[0].strip())
                high_sys = float(high.split(' ')[0].split("/")[0].strip())
                
                if latest.value_systolic > high_sys:
                    trend = "up"
                elif latest.value_systolic < low_sys:
                    trend = "down"
        
        elif latest.type.normal_range:
            range_str = latest.type.normal_range
            try:
                low, high = range_str.split(" - ")
                range_min = float(low.strip())
                range_max = float(high.split(" ")[0].strip())                
                
                if latest.value > range_max:
                    trend = "up"
                elif latest.value < range_min:
                    trend = "down"
            except (ValueError, AttributeError):
                trend = "stable"
            
        data_trends.append({
            "healthdata": latest,
            "trend": trend,
        })
          
    return data_trends