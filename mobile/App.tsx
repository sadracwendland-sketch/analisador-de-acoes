import React, { useMemo, useState } from 'react';
import { ActivityIndicator, SafeAreaView, ScrollView, StatusBar, StyleSheet, Text, TextInput, TouchableOpacity, useColorScheme, View } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const periods = ['1m', '5m', '1h', '1d', '1y'];
const screenWidth = Dimensions.get('window').width - 24;

type Analysis = any;

export default function App() {
  const theme = useColorScheme();
  const dark = theme !== 'light';
  const [ticker, setTicker] = useState('PETR4.SA');
  const [period, setPeriod] = useState('1d');
  const [capital, setCapital] = useState('100000');
  const [horizon, setHorizon] = useState('7');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const colors = useMemo(() => ({
    bg: dark ? '#020617' : '#f8fafc',
    card: dark ? '#0f172a' : '#ffffff',
    fg: dark ? '#e2e8f0' : '#0f172a',
    sub: dark ? '#94a3b8' : '#475569',
    green: '#22c55e',
    red: '#ef4444',
    yellow: '#f59e0b',
    blue: '#38bdf8'
  }), [dark]);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = `${API_BASE_URL}/api/analyze?ticker=${encodeURIComponent(ticker)}&period=${period}&capital=${capital}&horizon=${horizon}`;
      const res = await fetch(url);
      
      if (!res.ok) {
        const errorText = await res.text();
        setError(`Erro HTTP ${res.status}: ${errorText || res.statusText}`);
        console.error(`HTTP Error: ${res.status} ${res.statusText}`);
        return;
      }
      
      const json = await res.json();
      setData(json);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      setError(`Erro ao conectar com a API: ${errorMsg}`);
      console.error('Erro ao buscar análise:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    const items = (data?.price_history || []).slice(-24);
    return {
      labels: items.map((_: any, idx: number) => `${idx + 1}`),
      datasets: [{ data: items.map((x: any) => x.close || 0) || [0] }],
    };
  }, [data]);

  const btData = useMemo(() => {
    const items = (data?.backtest?.equity_curve || []).slice(-24);
    return {
      labels: items.map((_: any, idx: number) => `${idx + 1}`),
      datasets: [
        { data: items.map((x: any) => x.strategy || 0), color: () => colors.green },
        { data: items.map((x: any) => x.ibov || 0), color: () => colors.blue },
      ],
      legend: ['Estratégia', 'IBOV'],
    };
  }, [data, colors]);

  const signalColor = data?.signal?.label === 'COMPRA' ? colors.green : data?.signal?.label === 'VENDA' ? colors.red : colors.yellow;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      <StatusBar barStyle={dark ? 'light-content' : 'dark-content'} />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={[styles.title, { color: colors.fg }]}>📱 Stock Analyzer Pro</Text>
        <View style={[styles.card, { backgroundColor: colors.card }]}> 
          <Text style={[styles.label, { color: colors.sub }]}>Ticker</Text>
          <TextInput value={ticker} onChangeText={setTicker} style={[styles.input, { color: colors.fg, borderColor: colors.sub }]} placeholder="PETR4.SA" placeholderTextColor={colors.sub} />
          <Text style={[styles.label, { color: colors.sub }]}>Período</Text>
          <View style={[styles.pickerWrap, { borderColor: colors.sub }]}> 
            <Picker selectedValue={period} onValueChange={(value) => setPeriod(String(value))} dropdownIconColor={colors.fg} style={{ color: colors.fg }}>
              {periods.map((item) => <Picker.Item key={item} label={item} value={item} />)}
            </Picker>
          </View>
          <Text style={[styles.label, { color: colors.sub }]}>Capital</Text>
          <TextInput value={capital} onChangeText={setCapital} keyboardType="numeric" style={[styles.input, { color: colors.fg, borderColor: colors.sub }]} />
          <Text style={[styles.label, { color: colors.sub }]}>Horizonte ML</Text>
          <TextInput value={horizon} onChangeText={setHorizon} keyboardType="numeric" style={[styles.input, { color: colors.fg, borderColor: colors.sub }]} />
          <TouchableOpacity style={[styles.button, { backgroundColor: colors.green }]} onPress={runAnalysis}>
            <Text style={styles.buttonText}>Analisar</Text>
          </TouchableOpacity>
        </View>

        {loading && <ActivityIndicator size="large" color={colors.green} style={{ marginTop: 20 }} />}

        {error && (
          <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.red, borderWidth: 1 }]}>
            <Text style={[styles.label, { color: colors.red }]}>⚠️ Erro</Text>
            <Text style={[styles.sub, { color: colors.fg }]}>{error}</Text>
          </View>
        )}

        {data && !loading && (
          <>
            <View style={[styles.card, { backgroundColor: colors.card }]}> 
              <Text style={[styles.signal, { color: signalColor }]}>{data.signal.emoji} {data.signal.label}</Text>
              <Text style={[styles.kpi, { color: colors.fg }]}>{data.currency} {Number(data.last_price).toFixed(2)}</Text>
              <Text style={[styles.sub, { color: colors.sub }]}>Confiança {Number(data.signal.confidence).toFixed(1)}% · Previsão {data.forecast.expected_return_pct}%</Text>
            </View>

            <View style={[styles.card, { backgroundColor: colors.card }]}> 
              <Text style={[styles.section, { color: colors.fg }]}>Preço</Text>
              <LineChart
                data={chartData}
                width={screenWidth}
                height={220}
                withDots={false}
                bezier
                chartConfig={{
                  backgroundColor: colors.card,
                  backgroundGradientFrom: colors.card,
                  backgroundGradientTo: colors.card,
                  decimalPlaces: 2,
                  color: () => colors.blue,
                  labelColor: () => colors.sub,
                  propsForBackgroundLines: { stroke: '#334155' },
                }}
                style={styles.chart}
              />
            </View>

            <View style={[styles.card, { backgroundColor: colors.card }]}> 
              <Text style={[styles.section, { color: colors.fg }]}>Risco</Text>
              <Text style={[styles.sub, { color: colors.sub }]}>Stop-loss: {data.risk.stop_loss_pct}% · VaR95: {data.risk.value_at_risk_95_pct}%</Text>
              <Text style={[styles.sub, { color: colors.sub }]}>Position sizing: {data.risk.position_size_shares} ações · Budget: {data.risk.risk_budget}</Text>
            </View>

            <View style={[styles.card, { backgroundColor: colors.card }]}> 
              <Text style={[styles.section, { color: colors.fg }]}>Backtest</Text>
              <LineChart
                data={btData}
                width={screenWidth}
                height={220}
                withDots={false}
                chartConfig={{
                  backgroundColor: colors.card,
                  backgroundGradientFrom: colors.card,
                  backgroundGradientTo: colors.card,
                  decimalPlaces: 2,
                  color: () => colors.green,
                  labelColor: () => colors.sub,
                  propsForBackgroundLines: { stroke: '#334155' },
                }}
                style={styles.chart}
              />
              <Text style={[styles.sub, { color: colors.sub }]}>Sharpe: {data.backtest.stats.sharpe_ratio} · Max DD: {data.backtest.stats.max_drawdown_pct}%</Text>
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scroll: { padding: 12, paddingBottom: 40 },
  title: { fontSize: 28, fontWeight: '800', marginBottom: 12 },
  card: { borderRadius: 18, padding: 16, marginBottom: 12 },
  label: { marginBottom: 6, marginTop: 6, fontSize: 13, fontWeight: '600' },
  input: { borderWidth: 1, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, fontSize: 16 },
  pickerWrap: { borderWidth: 1, borderRadius: 12, overflow: 'hidden' },
  button: { marginTop: 16, borderRadius: 14, paddingVertical: 14, alignItems: 'center' },
  buttonText: { color: '#020617', fontWeight: '800', fontSize: 16 },
  signal: { fontSize: 26, fontWeight: '800' },
  kpi: { fontSize: 30, fontWeight: '800', marginTop: 6 },
  sub: { fontSize: 14, marginTop: 6, lineHeight: 20 },
  section: { fontSize: 20, fontWeight: '800', marginBottom: 8 },
  chart: { borderRadius: 16 }
});
