from ..models import HealthData

def group_compare_healthdata(healthdata: list[HealthData]):
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