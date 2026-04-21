import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface PredictionResult {
  scorePrediction: string;
  image_url: string;
}

interface ClassifierState {
  imageUrl: string | null;
  prediction: PredictionResult | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: ClassifierState = {
  imageUrl: null,
  prediction: null,
  isLoading: false,
  error: null,
};

export const classifyImage = createAsyncThunk(
  'classifier/classify',
  async (formData: FormData) => {
    const response = await fetch('/predictImage', {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    return data;
  }
);

const classifierSlice = createSlice({
  name: 'classifier',
  initialState,
  reducers: {
    setSelectedFile: (state, action: PayloadAction<{ url: string }>) => {
      state.imageUrl = action.payload.url;
      state.prediction = null;
      state.error = null;
    },
    clearPrediction: (state) => {
      state.imageUrl = null;
      state.prediction = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(classifyImage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(classifyImage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.prediction = action.payload;
      })
      .addCase(classifyImage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Ошибка классификации';
      });
  },
});

export const { setSelectedFile, clearPrediction } = classifierSlice.actions;
export default classifierSlice.reducer;