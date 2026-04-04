import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

@dataclass
class LLMResponse:
    content: str
    confidence: float
    metadata: Dict[str, Any]
    timestamp: datetime
    model_used: str
    tokens_used: int
    cost: float = 0.0

@dataclass
class TradingInsight:
    insight_type: str
    content: str
    confidence: float
    symbols: List[str]
    timeframe: str
    reasoning: str
    timestamp: datetime

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass

class DummyProvider(LLMProvider):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        return LLMResponse(
            content="AI service not configured",
            confidence=0.0,
            metadata={'error': 'No API key'},
            timestamp=datetime.now(),
            model_used='dummy',
            tokens_used=0
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        return {'provider': 'None', 'model': 'N/A', 'max_tokens': 0, 'supports_functions': False}

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        try:
            import openai
            openai.api_key = api_key
            self.client = openai
        except ImportError:
            raise ImportError("OpenAI package not installed")
    
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                confidence=0.8,
                metadata={'finish_reason': response.choices[0].finish_reason},
                timestamp=datetime.now(),
                model_used=self.model,
                tokens_used=response.usage.total_tokens,
                cost=0.0
            )
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        return {'provider': 'OpenAI', 'model': self.model, 'max_tokens': 4096, 'supports_functions': True}
    
    def _calculate_cost(self, usage) -> float:
        return 0.0

class LocalLLMProvider(LLMProvider):
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
        except ImportError:
            raise ImportError("Transformers not installed")
    
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        return LLMResponse(content="Local LLM not available", confidence=0.0, metadata={}, timestamp=datetime.now(), model_used=self.model_name, tokens_used=0)
    
    def get_model_info(self) -> Dict[str, Any]:
        return {'provider': 'Local', 'model': self.model_name, 'max_tokens': 512, 'supports_functions': False}

class LLMIntegration:
    def __init__(self, provider: str = "openai", api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.logger = logging.getLogger(__name__)
        
        # Try to get API key from environment variable if not provided
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
        
        self.provider = self._initialize_provider(provider, api_key, model)
        self._init_langchain()
        
        self.trading_prompts = {
            'market_analysis': self._get_market_analysis_prompt(),
            'signal_generation': self._get_signal_generation_prompt(),
            'risk_assessment': self._get_risk_assessment_prompt(),
            'portfolio_optimization': self._get_portfolio_optimization_prompt()
        }
    
    def _initialize_provider(self, provider: str, api_key: str, model: str) -> LLMProvider:
        if provider.lower() == "openai":
            if not api_key:
                self.logger.warning("No OpenAI API key, using dummy provider")
                return DummyProvider()
            return OpenAIProvider(api_key, model)
        elif provider.lower() == "local":
            return LocalLLMProvider(model)
        else:
            self.logger.warning(f"Unknown provider: {provider}, using dummy")
            return DummyProvider()
    
    def _init_langchain(self):
        try:
            from langchain.llms import OpenAI
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
            from langchain.memory import ConversationBufferMemory
            
            self.langchain_available = True
            self.memory = ConversationBufferMemory()
        except ImportError:
            self.logger.warning("LangChain not available")
            self.langchain_available = False
    
    def analyze_market_data(self, market_data: pd.DataFrame, symbols: List[str]) -> TradingInsight:
        return self._create_default_insight('analysis', symbols)
    
    def generate_trading_signals(self, factor_data: pd.DataFrame, price_data: pd.DataFrame, strategy_context: str = "") -> TradingInsight:
        return self._create_default_insight('signal', list(factor_data.columns) if factor_data is not None else [])
    
    def assess_risk(self, portfolio_data: Dict[str, Any], market_conditions: Dict[str, Any]) -> TradingInsight:
        return self._create_default_insight('risk_warning', [])
    
    def optimize_portfolio(self, current_weights: Dict[str, float], factor_scores: Dict[str, Dict[str, float]], constraints: Dict[str, Any]) -> TradingInsight:
        return self._create_default_insight('recommendation', list(current_weights.keys()) if current_weights else [])
    
    def answer_trading_question(self, question: str, context_data: Dict[str, Any] = None) -> LLMResponse:
        return LLMResponse(content="AI service not configured", confidence=0.0, metadata={}, timestamp=datetime.now(), model_used='none', tokens_used=0)
    
    def _create_default_insight(self, insight_type: str, symbols: List[str]) -> TradingInsight:
        return TradingInsight(
            insight_type=insight_type,
            content="AI feature not available. Configure OPENAI_API_KEY to enable.",
            confidence=0.0,
            symbols=symbols,
            timeframe='current',
            reasoning="LLM not configured",
            timestamp=datetime.now()
        )
    
    def _get_market_analysis_prompt(self) -> str:
        return "You are a financial analyst."
    
    def _get_signal_generation_prompt(self) -> str:
        return "Generate trading signals."
    
    def _get_risk_assessment_prompt(self) -> str:
        return "Assess portfolio risk."
    
    def _get_portfolio_optimization_prompt(self) -> str:
        return "Optimize portfolio."
    
    def get_provider_info(self) -> Dict[str, Any]:
        return self.provider.get_model_info()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        return {'provider': self.provider.get_model_info()['provider'], 'model': self.provider.get_model_info()['model'], 'timestamp': datetime.now()}