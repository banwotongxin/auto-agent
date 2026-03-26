//经纬度接口，与后端Pydantic对应
export interface Location {
  latitude: number;
  longitude: number;
}

//景点信息，与后端Pydantic中的Optional对应
export interface Attraction {
  name: string;
  address: string;
  location: Location;
  visit_duration: number;
  description: string;
  category?: string;
  rating?: number;//评分
  image_url?: string;
  ticket_price?: number;
}

//餐饮信息
export interface Meal {
  name: string;
  address: string;
  location: Location;
  description: string;//餐厅介绍
  avg_cost: number;//人均消费
  cuisine_type: string;//菜系类型
  rating?: number;//评分
  image_url?: string;
  opening_hours?: string;//营业时间
  reservation_phone?: string;//预约电话
}

//酒店信息
export interface Hotel {
  name: string;
  address: string;
  location: Location;
  description: string;//酒店介绍
  rating?: number;//评分
  image_url?: string;
  price_range?: string;//价格范围
  amenities?: string[];//设施服务
  check_in_time?: string;//入住时间
  check_out_time?: string;//退房时间
}

//交通信息
export interface Transportation {
  type: string;//交通类型
  departure: string;//出发地
  arrival: string;//目的地
  duration: number;//交通时长
  cost: number;//交通费用
  departure_location: Location;//出发地
  arrival_location: Location;//目的地
  departure_time?: string;//出发时间
  arrival_time?: string;//到达时间
  distance?: number;//距离
  route_instructions?: string;//路线指引
}

//预算范围
export interface Budget {
  total: number;//总预算
  currency: string;//货币单位
  attractions?: number;//景点预算
  meals?: number;//餐饮预算
  hotels?: number;//酒店预算
  transportation?: number;//交通预算
  shopping?: number;//购物预算
  other?: number;//其他预算
  remaining?: number;//剩余预算
}

//天气信息
export interface WeatherInfo {
  date: string;//日期
  temperature: number;
  condition: string;//天气状况
  location: Location;
  temp_min: number;//最低温度
  temp_max: number;//最高温度
  tips?: string;//天气建议
}

//每日行程计划
export interface DayPlan {
  day: number;//第几天
  date: string;
  title: string;//行程主题
  attractions: Attraction[];//当日景点
  meals: Meal[];//当日餐饮
  transportation: Transportation[];//当日交通
  hotels: Hotel[];//当日酒店
  notes?: string;//备注
}

export interface TripPlan {
  city: string;
  start_date: string;
  end_date: string;
  total_days: number;//总天数
  days: DayPlan[];
  weather_info: WeatherInfo[];
  overall_suggestion: string;//总体建议
  budget?: Budget;
  plan_id?: string;//计划id
  user_id?: string;//用户id
  created_at?: string;//创建时间
}

//生成旅行计划的请求参数
export interface TripPlanRequest {
  city: string;
  start_date: string;
  end_date: string;
  days: number;
  preferences: string;
  budget: string;
  transportation: string;
  accommodation: string;
  travelers?: number;//旅行人数
  special_needs?: string;//特殊要求
}