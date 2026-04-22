import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface PredictionResult {
  predictedLabel: string;
  confidence: string;
  imageUrl: string;
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
  extraReducers: (builder) => {
    builder
      .addMatcher(
        (action): action is { type: 'classifier/classify/pending' } =>
          action.type === 'classifier/classify/pending',
        (state) => {
          state.isLoading = true;
          state.error = null;
        }
      )
      .addMatcher(
        (
          action
        ): action is {
          type: 'classifier/classify/fulfilled';
          payload: PredictionResult;
        } => action.type === 'classifier/classify/fulfilled',
        (state, action) => {
          state.isLoading = false;
          state.prediction = action.payload;
          state.imageUrl = action.payload.imageUrl;
          state.error = null;
        }
      )
      .addMatcher(
        (
          action
        ): action is {
          type: 'classifier/classify/rejected';
          payload: { message: string };
        } => action.type === 'classifier/classify/rejected',
        (state, action) => {
          state.isLoading = false;
          state.error = action.payload.message;
        }
      );
  },
});

export const { setSelectedFile, clearPrediction } = classifierSlice.actions;
export default classifierSlice.reducer;