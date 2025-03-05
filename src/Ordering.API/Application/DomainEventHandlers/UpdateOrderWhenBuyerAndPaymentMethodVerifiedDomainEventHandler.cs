using System.Diagnostics;

namespace eShop.Ordering.API.Application.DomainEventHandlers;

public class UpdateOrderWhenBuyerAndPaymentMethodVerifiedDomainEventHandler : INotificationHandler<BuyerAndPaymentMethodVerifiedDomainEvent>
{
    private static readonly ActivitySource _activitySource = new("eShop.Ordering.API.Application.DomainEventHandlers.UpdateOrderWhenBuyerAndPaymentMethodVerifiedDomainEventHandler");
    private readonly IOrderRepository _orderRepository;
    private readonly ILogger _logger;

    public UpdateOrderWhenBuyerAndPaymentMethodVerifiedDomainEventHandler(
        IOrderRepository orderRepository,
        ILogger<UpdateOrderWhenBuyerAndPaymentMethodVerifiedDomainEventHandler> logger)
    {
        _orderRepository = orderRepository ?? throw new ArgumentNullException(nameof(orderRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    // Domain Logic comment:
    // When the Buyer and Buyer's payment method have been created or verified that they existed, 
    // then we can update the original Order with the BuyerId and PaymentId (foreign keys)
    public async Task Handle(BuyerAndPaymentMethodVerifiedDomainEvent domainEvent, CancellationToken cancellationToken)
    {
        using var activity = _activitySource.StartActivity("UpdateOrderWhenBuyerAndPaymentMethodVerifiedDomainEventHandler Handler");
        var orderToUpdate = await _orderRepository.GetAsync(domainEvent.OrderId);
        activity?.AddEvent(new ActivityEvent(
            "Get order to update",
            DateTime.UtcNow,
            new ActivityTagsCollection{
                { "order.id", orderToUpdate.Id }
            }
        ));
        orderToUpdate.SetPaymentMethodVerified(domainEvent.Buyer.Id, domainEvent.Payment.Id); 

        activity?.AddEvent(new ActivityEvent(
            "Update order payment method",
            DateTime.UtcNow,
            new ActivityTagsCollection{
                { "order.id", domainEvent.OrderId },
                { "payment.id", domainEvent.Payment.Id },
                { "buyer.id", domainEvent.Buyer.Id }
            }
        ));
        OrderingApiTrace.LogOrderPaymentMethodUpdated(_logger, domainEvent.OrderId, nameof(domainEvent.Payment), domainEvent.Payment.Id);
    }
}
