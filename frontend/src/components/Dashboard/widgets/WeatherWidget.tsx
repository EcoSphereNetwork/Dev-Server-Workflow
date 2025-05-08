/**
 * Weather-Widget
 * 
 * Zeigt Wetterdaten an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Wetter-Typ
interface Weather {
  location: string;
  temperature: number;
  condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy' | 'snowy';
  humidity: number;
  windSpeed: number;
  forecast: Array<{
    day: string;
    temperature: number;
    condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy' | 'snowy';
  }>;
}

// Styled-Components für das Widget
const WeatherContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const CurrentWeather = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const WeatherInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const Location = styled.div`
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

const Temperature = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xxl};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin: ${props => props.theme.spacing.xs} 0;
`;

const Condition = styled.div`
  font-size: ${props => props.theme.typography.fontSize.md};
  color: ${props => props.theme.colors.text.secondary};
`;

const WeatherIcon = styled.div`
  font-size: 4rem;
`;

const WeatherDetails = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const WeatherDetail = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.md};
  flex: 1;
  
  &:not(:last-child) {
    margin-right: ${props => props.theme.spacing.sm};
  }
`;

const DetailLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const DetailValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const Forecast = styled.div`
  display: flex;
  justify-content: space-between;
  overflow-x: auto;
  padding-bottom: ${props => props.theme.spacing.sm};
  
  /* Scrollbar-Styling */
  &::-webkit-scrollbar {
    height: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.background.paper};
    border-radius: 2px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.primary};
    border-radius: 2px;
  }
`;

const ForecastDay = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.md};
  min-width: 80px;
  
  &:not(:last-child) {
    margin-right: ${props => props.theme.spacing.sm};
  }
`;

const DayName = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const DayIcon = styled.div`
  font-size: 1.5rem;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const DayTemperature = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

// Weather-Widget-Props
export interface WeatherWidgetProps extends Omit<WidgetProps, 'children'> {}

// Weather-Widget-Komponente
export const WeatherWidget: React.FC<WeatherWidgetProps> = (props) => {
  // State für Wetter
  const [weather, setWeather] = useState<Weather | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Simuliere Laden von Wetterdaten
  useEffect(() => {
    const mockWeather: Weather = {
      location: 'Berlin, Deutschland',
      temperature: 22,
      condition: 'sunny',
      humidity: 65,
      windSpeed: 12,
      forecast: [
        { day: 'Heute', temperature: 22, condition: 'sunny' },
        { day: 'Mo', temperature: 24, condition: 'sunny' },
        { day: 'Di', temperature: 20, condition: 'cloudy' },
        { day: 'Mi', temperature: 18, condition: 'rainy' },
        { day: 'Do', temperature: 17, condition: 'rainy' },
        { day: 'Fr', temperature: 19, condition: 'cloudy' },
        { day: 'Sa', temperature: 21, condition: 'sunny' },
      ],
    };
    
    // Simuliere Laden
    setTimeout(() => {
      setWeather(mockWeather);
      setLoading(false);
    }, 1000);
  }, []);
  
  // Wetter-Icon basierend auf Bedingung
  const getWeatherIcon = (condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy' | 'snowy'): string => {
    switch (condition) {
      case 'sunny':
        return '☀️';
      case 'cloudy':
        return '☁️';
      case 'rainy':
        return '🌧️';
      case 'stormy':
        return '⛈️';
      case 'snowy':
        return '❄️';
      default:
        return '☀️';
    }
  };
  
  // Bedingung als Text
  const getConditionText = (condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy' | 'snowy'): string => {
    switch (condition) {
      case 'sunny':
        return 'Sonnig';
      case 'cloudy':
        return 'Bewölkt';
      case 'rainy':
        return 'Regnerisch';
      case 'stormy':
        return 'Stürmisch';
      case 'snowy':
        return 'Schnee';
      default:
        return 'Sonnig';
    }
  };
  
  return (
    <Widget {...props}>
      {loading ? (
        <div>Lade Wetterdaten...</div>
      ) : weather ? (
        <WeatherContainer>
          <CurrentWeather>
            <WeatherInfo>
              <Location>{weather.location}</Location>
              <Temperature>{weather.temperature}°C</Temperature>
              <Condition>{getConditionText(weather.condition)}</Condition>
            </WeatherInfo>
            <WeatherIcon>{getWeatherIcon(weather.condition)}</WeatherIcon>
          </CurrentWeather>
          
          <WeatherDetails>
            <WeatherDetail>
              <DetailLabel>Luftfeuchtigkeit</DetailLabel>
              <DetailValue>{weather.humidity}%</DetailValue>
            </WeatherDetail>
            <WeatherDetail>
              <DetailLabel>Windgeschwindigkeit</DetailLabel>
              <DetailValue>{weather.windSpeed} km/h</DetailValue>
            </WeatherDetail>
          </WeatherDetails>
          
          <Forecast>
            {weather.forecast.map((day, index) => (
              <ForecastDay key={index}>
                <DayName>{day.day}</DayName>
                <DayIcon>{getWeatherIcon(day.condition)}</DayIcon>
                <DayTemperature>{day.temperature}°C</DayTemperature>
              </ForecastDay>
            ))}
          </Forecast>
        </WeatherContainer>
      ) : (
        <div>Keine Wetterdaten verfügbar.</div>
      )}
    </Widget>
  );
};

export default WeatherWidget;