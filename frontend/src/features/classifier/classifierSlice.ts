import { createSlice } from '@reduxjs/toolkit';
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
});

export const { setSelectedFile, clearPrediction } = classifierSlice.actions;
export default classifierSlice.reducer;