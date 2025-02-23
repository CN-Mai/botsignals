from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from datetime import datetime, timedelta
import json
import logging
from payment_handlers import PaymentProcessor

logger = logging.getLogger(__name__)

class SubscriptionHandler:
    def __init__(self, config, db_session):
        self.config = config
        self.db_session = db_session
        self.payment_processor = PaymentProcessor(config)
    
    async def handle_subscribe_command(self, update: Update, context: CallbackContext):
        """Handle the /subscribe command"""
        keyboard = [
            [
                InlineKeyboardButton("Monthly - $29.99", callback_data='sub_monthly'),
                InlineKeyboardButton("Quarterly - $79.99", callback_data='sub_quarterly')
            ],
            [
                InlineKeyboardButton("Annual - $299.99", callback_data='sub_annual')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🌟 Choose your Premium Subscription Plan:\n\n"
            "All plans include:\n"
            "• Advanced AI-powered signals\n"
            "• Priority alerts\n"
            "• Detailed market analysis\n"
            "• Custom alert settings\n"
            "• 24/7 support\n\n"
            "Select your preferred plan:",
            reply_markup=reply_markup
        )
    
    async def handle_subscription_callback(self, update: Update, context: CallbackContext):
        """Handle subscription plan selection"""
        query = update.callback_query
        await query.answer()
        
        plan = query.data.split('_')[1]
        amount = self.config.SUBSCRIPTION_PRICES[plan]
        
        # Generate payment options
        payment_options = await self.payment_processor.generate_payment_options(
            update.effective_user.id,
            amount
        )
        
        if not payment_options:
            await query.edit_message_text("Error generating payment options. Please try again later.")
            return
        
        # Create payment selection keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    "Pay with MetaMask (ETH)", 
                    callback_data=f'pay_metamask_{plan}'
                )
            ],
            [
                InlineKeyboardButton(
                    "Pay with Phantom (SOL)", 
                    callback_data=f'pay_phantom_{plan}'
                )
            ],
            [
                InlineKeyboardButton(
                    "Pay with Binance", 
                    callback_data=f'pay_binance_{plan}'
                )
            ]
        ]
        
        # Store payment options in context for later use
        context.user_data['payment_options'] = payment_options
        context.user_data['selected_plan'] = plan
        
        await query.edit_message_text(
            f"💎 Selected plan: {plan.capitalize()}\n"
            f"Amount: ${amount}\n\n"
            "Choose your payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_payment_method_callback(self, update: Update, context: CallbackContext):
        """Handle payment method selection"""
        query = update.callback_query
        await query.answer()
        
        method, plan = query.data.split('_')[1:]
        payment_options = context.user_data.get('payment_options')
        
        if not payment_options:
            await query.edit_message_text("Payment session expired. Please start again with /subscribe")
            return
        
        if method == 'metamask':
            payment_data = payment_options['metamask']
            message = (
                "🦊 MetaMask Payment Instructions:\n\n"
                f"Amount: {payment_data['amount']:.6f} ETH\n"
                f"Address: `{payment_data['address']}`\n\n"
                "1. Open MetaMask\n"
                "2. Send the exact amount to the address above\n"
                "3. After sending, click 'Verify Payment' below"
            )
        
        elif method == 'phantom':
            payment_data = payment_options['phantom']
            message = (
                "👻 Phantom Wallet Payment Instructions:\n\n"
                f"Amount: {payment_data['amount']:.6f} SOL\n"
                f"Address: `{payment_data['address']}`\n\n"
                "1. Open Phantom Wallet\n"
                "2. Send the exact amount to the address above\n"
                "3. After sending, click 'Verify Payment' below"
            )
        
        else:  # binance
            payment_data = payment_options['binance']
            message = (
                "💰 Binance Pay Instructions:\n\n"
                f"Amount: {payment_data['amount']:.6f} BNB\n"
                "1. Open Binance App\n"
                "2. Scan the QR code below\n"
                "3. Complete the payment in your Binance App\n"
                "4. After paying, click 'Verify Payment' below"
            )
        
        keyboard = [[
            InlineKeyboardButton(
                "Verify Payment", 
                callback_data=f'verify_{method}_{plan}'
            )
        ]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # If Binance Pay, send QR code as separate message
        if method == 'binance':
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=payment_data['qr_code']
            )
    
    async def handle_payment_verification(self, update: Update, context: CallbackContext):
        """Handle payment verification"""
        query = update.callback_query
        await query.answer()
        
        method, plan = query.data.split('_')[1:]
        payment_options = context.user_data.get('payment_options')
        
        if not payment_options:
            await query.edit_message_text("Payment session expired. Please start again with /subscribe")
            return
        
        # Show processing message
        await query.edit_message_text(
            "⏳ Verifying payment... Please wait..."
        )
        
        # Verify payment
        payment_verified = await self.payment_processor.verify_payment({
            'method': method,
            'plan': plan,
            **payment_options[method]
        })
        
        if payment_verified:
            # Update user subscription
            user = self.db_session.query(User).filter_by(
                telegram_id=update.effective_user.id
            ).first()
            
            duration_days = {
                'monthly': 30,
                'quarterly': 90,
                'annual': 365
            }[plan]
            
            user.is_premium = True
            user.subscription_end = datetime.utcnow() + timedelta(days=duration_days)
            self.db_session.commit()
            
            await query.edit_message_text(
                "✅ Payment verified! Your premium subscription is now active.\n\n"
                f"Subscription end date: {user.subscription_end.strftime('%Y-%m-%d')}\n\n"
                "Enjoy your premium features! Use /help to see all available commands."
            )
        else:
            await query.edit_message_text(
                "❌ Payment verification failed. If you believe this is an error, "
                "please contact support with your transaction details.\n\n"
                "You can try again by using the /subscribe command."
            )